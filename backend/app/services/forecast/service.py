from __future__ import annotations

import json
from datetime import UTC, datetime

import numpy as np
import pandas as pd

from app.schemas.models import Forecast5DResult, ForecastRequest, ForecastScenario
from app.services.backtest.engine import candles_to_frame
from app.services.forecast.feature_engineering import build_feature_frame
from app.services.forecast.models import create_model_bundle, normalize_probabilities
from app.storage.repositories import SQLiteRepository


FEATURE_COLUMNS = [
    "return_1",
    "return_5",
    "volatility_10",
    "volatility_20",
    "sma_ratio",
    "volume_ratio",
    "range_ratio",
]


class ForecastService:
    def __init__(self, repository: SQLiteRepository) -> None:
        self.repository = repository

    def generate(
        self,
        request: ForecastRequest,
        candles: list[dict] | list,
        source_status: str,
    ) -> Forecast5DResult:
        frame = candles_to_frame(candles)
        features = build_feature_frame(frame)
        if len(features) < 60:
            return self._heuristic_forecast(request.symbol, frame, source_status)

        model_bundle = create_model_bundle()
        x_train = features[FEATURE_COLUMNS]
        y_class = features["future_class"]
        y_reg = features["future_return_5"]
        model_bundle.classifier.fit(x_train, y_class)
        model_bundle.regressor.fit(x_train, y_reg)

        latest_features = x_train.iloc[[-1]]
        probabilities_raw = model_bundle.classifier.predict_proba(latest_features)[0]
        probabilities = normalize_probabilities(np.array(probabilities_raw))
        expected_return = float(model_bundle.regressor.predict(latest_features)[0])

        latest_close = float(frame["close"].iloc[-1])
        result = Forecast5DResult(
            symbol=request.symbol,
            generated_at=datetime.now(tz=UTC),
            model_family=model_bundle.family,
            source_status=source_status,
            expected_return_range=(round(expected_return - 0.03, 4), round(expected_return + 0.03, 4)),
            expected_price_range=(
                round(latest_close * (1 + expected_return - 0.03), 2),
                round(latest_close * (1 + expected_return + 0.03), 2),
            ),
            scenarios=[
                ForecastScenario(
                    label="bearish",
                    probability=round(probabilities[0], 4),
                    expected_return=round(expected_return - 0.04, 4),
                ),
                ForecastScenario(
                    label="neutral",
                    probability=round(probabilities[1], 4),
                    expected_return=round(expected_return, 4),
                ),
                ForecastScenario(
                    label="bullish",
                    probability=round(probabilities[2], 4),
                    expected_return=round(expected_return + 0.04, 4),
                ),
            ],
            rationale=[
                "The model uses recent returns, volatility, moving-average structure, and volume expansion.",
                "Forecast output is a scenario distribution over the next five trading sessions.",
            ],
            caveat="This forecast is a probabilistic research aid and not investment advice.",
        )
        self.repository.save_latest_forecast(request.symbol, json.dumps(result.model_dump(mode="json")))
        return result

    def latest(self, symbol: str) -> Forecast5DResult | None:
        payload = self.repository.get_latest_forecast(symbol)
        if not payload:
            return None
        return Forecast5DResult.model_validate(payload)

    def _heuristic_forecast(
        self,
        symbol: str,
        frame: pd.DataFrame,
        source_status: str,
    ) -> Forecast5DResult:
        returns = frame["close"].pct_change().dropna()
        momentum = float(returns.tail(10).mean())
        volatility = float(returns.tail(20).std() if len(returns) >= 20 else returns.std())
        expected_return = momentum * 5
        bear = max(0.15, min(0.6, 0.34 - momentum * 3))
        bull = max(0.15, min(0.6, 0.34 + momentum * 3))
        neutral = max(0.1, 1 - bear - bull)
        probabilities = normalize_probabilities(np.array([bear, neutral, bull]))
        last_close = float(frame["close"].iloc[-1])
        band = max(volatility * 4, 0.02)
        result = Forecast5DResult(
            symbol=symbol,
            generated_at=datetime.now(tz=UTC),
            model_family="heuristic_fallback",
            source_status=source_status,
            expected_return_range=(round(expected_return - band, 4), round(expected_return + band, 4)),
            expected_price_range=(
                round(last_close * (1 + expected_return - band), 2),
                round(last_close * (1 + expected_return + band), 2),
            ),
            scenarios=[
                ForecastScenario(
                    label="bearish",
                    probability=round(probabilities[0], 4),
                    expected_return=round(expected_return - band, 4),
                ),
                ForecastScenario(
                    label="neutral",
                    probability=round(probabilities[1], 4),
                    expected_return=round(expected_return, 4),
                ),
                ForecastScenario(
                    label="bullish",
                    probability=round(probabilities[2], 4),
                    expected_return=round(expected_return + band, 4),
                ),
            ],
            rationale=[
                "There was not enough training history for the full model, so a heuristic fallback was used.",
                "Recent momentum and volatility are used to shape the five-session scenario band.",
            ],
            caveat="This forecast is a probabilistic research aid and not investment advice.",
        )
        self.repository.save_latest_forecast(symbol, json.dumps(result.model_dump(mode="json")))
        return result
