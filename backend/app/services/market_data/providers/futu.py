from __future__ import annotations

import math
import os
from datetime import UTC, datetime
from pathlib import Path

from app.schemas.models import CandlePoint, CandleSeries, MarketMetric, MarketOverview, MarketSnapshot, OverviewSection
from app.services.market_data.symbol import display_name_for, to_futu_code

from .base import MarketDataProvider, ProviderUnavailableError


def _fallback_change_percent(raw_change_percent: float | int | None, price: float, previous_close: float) -> float:
    if raw_change_percent is not None and math.isfinite(float(raw_change_percent)):
        if abs(float(raw_change_percent)) > 1e-9:
            return float(raw_change_percent)
        if previous_close <= 0:
            return 0.0
        if abs(price - previous_close) <= 1e-9:
            return 0.0
    if previous_close <= 0:
        return 0.0
    return (price - previous_close) / previous_close * 100


class FutuMarketDataProvider(MarketDataProvider):
    source_name = "futu"
    region_symbols = {
        "US": [("US.SPY", "S&P 500"), ("US.QQQ", "Nasdaq 100"), ("US.DIA", "Dow Jones")],
        "HK": [("HK.800000", "Hang Seng"), ("HK.800700", "Hang Seng Tech"), ("HK.800100", "HSCEI")],
        "CN": [("SH.000001", "SSE Composite"), ("SZ.399001", "SZSE Component"), ("SZ.399006", "ChiNext")],
    }

    def __init__(self, host: str, port: int, sdk_appdata_path: Path) -> None:
        self.host = host
        self.port = port
        self.sdk_appdata_path = sdk_appdata_path

    def _prepare_sdk_environment(self) -> None:
        self.sdk_appdata_path.mkdir(parents=True, exist_ok=True)
        os.environ["APPDATA"] = str(self.sdk_appdata_path)
        os.environ["appdata"] = str(self.sdk_appdata_path)

    def _get_context(self):
        self._prepare_sdk_environment()
        try:
            from futu import OpenQuoteContext
        except ImportError as exc:
            raise ProviderUnavailableError(
                "futu package is not installed. Install futu-api and start OpenD."
            ) from exc
        return OpenQuoteContext(host=self.host, port=self.port)

    def get_market_overview(self, watchlist: list[str]) -> MarketOverview:
        sections = [self.get_overview_section(region) for region in self.region_symbols]
        snapshots = [self.get_snapshot(symbol) for symbol in watchlist]
        return MarketOverview(
            generated_at=datetime.now(tz=UTC),
            provider=self.source_name,
            source_status="live",
            sections=sections,
            top_news=[],
            watchlist=snapshots,
        )

    def get_overview_section(self, region: str) -> OverviewSection:
        metrics = self.region_symbols[region]
        with self._get_context() as quote_ctx:
            codes = [symbol for symbol, _ in metrics]
            ret, data = quote_ctx.get_market_snapshot(codes)
            if ret != 0:
                raise ProviderUnavailableError(str(data))
        section_metrics = []
        for row, (_, label) in zip(data.to_dict("records"), metrics, strict=False):
            price = float(row.get("last_price", 0.0))
            previous_close = float(row.get("prev_close_price", 0.0))
            section_metrics.append(
                MarketMetric(
                    label=label,
                    value=price,
                    change_percent=_fallback_change_percent(row.get("change_rate"), price, previous_close),
                    symbol=row["code"],
                )
            )
        return OverviewSection(
            region=region,
            title={"US": "US Session", "HK": "HK Session", "CN": "A-Share Session"}[region],
            source_status="live",
            metrics=section_metrics,
        )

    def get_snapshot(self, symbol: str) -> MarketSnapshot:
        normalized = to_futu_code(symbol)
        with self._get_context() as quote_ctx:
            ret, data = quote_ctx.get_market_snapshot([normalized])
            if ret != 0 or data.empty:
                raise ProviderUnavailableError(str(data))
            row = data.iloc[0]
        price = float(row.get("last_price", 0.0))
        previous_close = float(row.get("prev_close_price", 0.0))
        return MarketSnapshot(
            symbol=normalized,
            display_name=display_name_for(normalized),
            price=price,
            change=price - previous_close,
            change_percent=_fallback_change_percent(row.get("change_rate"), price, previous_close),
            previous_close=previous_close,
            open=float(row.get("open_price", 0.0)),
            high=float(row.get("high_price", 0.0)),
            low=float(row.get("low_price", 0.0)),
            volume=float(row.get("volume", 0.0)),
            turnover=float(row.get("turnover", 0.0)),
            timestamp=datetime.now(tz=UTC),
            market_state=str(row.get("sec_status", "UNKNOWN")),
            source_status="live",
        )

    def get_candles(self, symbol: str, interval: str = "1d", limit: int = 180) -> CandleSeries:
        normalized = to_futu_code(symbol)
        self._prepare_sdk_environment()
        try:
            from futu import AuType, KLType, SubType
        except ImportError as exc:
            raise ProviderUnavailableError(
                "futu package is not installed. Install futu-api and start OpenD."
            ) from exc

        interval_map = {
            "1d": (KLType.K_DAY, SubType.K_DAY),
            "1h": (KLType.K_60M, SubType.K_60M),
            "30m": (KLType.K_30M, SubType.K_30M),
            "15m": (KLType.K_15M, SubType.K_15M),
        }
        ktype, sub_type = interval_map.get(interval, (KLType.K_DAY, SubType.K_DAY))

        with self._get_context() as quote_ctx:
            ret, data = quote_ctx.subscribe([normalized], [sub_type], subscribe_push=False)
            if ret != 0:
                raise ProviderUnavailableError(str(data))
            ret, data = quote_ctx.get_cur_kline(
                normalized,
                num=limit,
                ktype=ktype,
                autype=AuType.QFQ,
            )
            if ret != 0:
                raise ProviderUnavailableError(str(data))

        points = [
            CandlePoint(
                timestamp=datetime.fromisoformat(str(row["time_key"])).replace(tzinfo=UTC),
                open=float(row["open"]),
                high=float(row["high"]),
                low=float(row["low"]),
                close=float(row["close"]),
                volume=float(row["volume"]),
            )
            for row in data.to_dict("records")
        ]
        return CandleSeries(symbol=normalized, interval=interval, source_status="live", points=points)
