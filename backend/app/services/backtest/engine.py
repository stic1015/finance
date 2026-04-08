from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import numpy as np
import pandas as pd

from app.schemas.models import BacktestMetrics, BacktestRequest, BacktestResult, EquityPoint
from app.services.backtest.strategies import STRATEGIES, build_signal_frame


def candles_to_frame(candles: list[dict] | list) -> pd.DataFrame:
    records = []
    for point in candles:
        if hasattr(point, "model_dump"):
            records.append(point.model_dump())
        else:
            records.append(point)
    frame = pd.DataFrame(records)
    frame["timestamp"] = pd.to_datetime(frame["timestamp"], utc=True)
    frame = frame.sort_values("timestamp").reset_index(drop=True)
    return frame


def validate_strategy_params(strategy: str, params: dict) -> dict:
    defaults = STRATEGIES[strategy].default_params
    merged = {**defaults, **params}
    if strategy == "moving_average_trend" and merged["fast_window"] >= merged["slow_window"]:
        raise ValueError("fast_window must be smaller than slow_window.")
    return merged


def run_backtest(request: BacktestRequest, candles: list[dict] | list) -> BacktestResult:
    params = validate_strategy_params(request.strategy, request.params)
    frame = candles_to_frame(candles)
    frame = frame[
        (frame["timestamp"] >= request.start_date) & (frame["timestamp"] <= request.end_date)
    ].copy()
    signal = build_signal_frame(frame, request.strategy, params)
    frame["signal"] = signal.shift(1).fillna(0.0)
    frame["returns"] = frame["close"].pct_change().fillna(0.0)

    total_cost = (request.fee_bps + request.slippage_bps) / 10_000
    trades = frame["signal"].diff().abs().fillna(0.0)
    frame["strategy_returns"] = frame["signal"] * frame["returns"] - trades * total_cost
    frame["equity"] = request.initial_capital * (1 + frame["strategy_returns"]).cumprod()
    frame["benchmark_equity"] = request.initial_capital * (1 + frame["returns"]).cumprod()

    daily = frame["strategy_returns"]
    wins = int((daily > 0).sum())
    downside = frame["equity"] / frame["equity"].cummax() - 1
    trade_count = int(trades.sum())
    equity_curve = [
        EquityPoint(
            timestamp=row["timestamp"].to_pydatetime().replace(tzinfo=UTC),
            equity=float(row["equity"]),
            benchmark_equity=float(row["benchmark_equity"]),
        )
        for _, row in frame.iterrows()
    ]

    sharpe = 0.0
    if float(daily.std()) > 0:
        sharpe = float(np.sqrt(252) * daily.mean() / daily.std())

    annualized = float(
        (frame["equity"].iloc[-1] / request.initial_capital) ** (252 / max(len(frame), 1)) - 1
    )
    metrics = BacktestMetrics(
        cumulative_return=float(frame["equity"].iloc[-1] / request.initial_capital - 1),
        annualized_return=annualized,
        sharpe_ratio=sharpe,
        max_drawdown=float(downside.min()),
        win_rate=float(wins / max((daily != 0).sum(), 1)),
        trade_count=trade_count,
        benchmark_return=float(frame["benchmark_equity"].iloc[-1] / request.initial_capital - 1),
    )

    return BacktestResult(
        job_id=str(uuid4()),
        symbol=request.symbol,
        strategy=request.strategy,
        benchmark_symbol=request.benchmark_symbol,
        started_at=datetime.now(tz=UTC),
        completed_at=datetime.now(tz=UTC),
        status="completed",
        metrics=metrics,
        equity_curve=equity_curve,
        params=params,
        caveats=[
            "Signals are shifted by one bar to reduce look-ahead bias.",
            "This backtest does not yet model survivorship bias across changing universes.",
        ],
    )
