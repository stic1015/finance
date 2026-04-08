from __future__ import annotations

import os
from datetime import UTC, datetime
from pathlib import Path

from app.schemas.models import CandlePoint, CandleSeries, MarketMetric, MarketOverview, MarketSnapshot, OverviewSection
from app.services.market_data.symbol import display_name_for, to_futu_code

from .base import MarketDataProvider, ProviderUnavailableError


class FutuMarketDataProvider(MarketDataProvider):
    source_name = "futu"
    region_symbols = {
        "US": [("US.SPY", "标普500"), ("US.QQQ", "纳指100"), ("US.DIA", "道琼斯")],
        "HK": [("HK.800000", "恒生指数"), ("HK.800700", "恒生科技"), ("HK.800100", "国企指数")],
        "CN": [("SH.000001", "上证综指"), ("SZ.399001", "深证成指"), ("SZ.399006", "创业板指")],
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
            section_metrics.append(
                MarketMetric(
                    label=label,
                    value=float(row.get("last_price", 0.0)),
                    change_percent=float(row.get("change_rate", 0.0)),
                    symbol=row["code"],
                )
            )
        return OverviewSection(
            region=region,
            title={"US": "美股时段", "HK": "港股时段", "CN": "A股时段"}[region],
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
        return MarketSnapshot(
            symbol=normalized,
            display_name=display_name_for(normalized),
            price=float(row.get("last_price", 0.0)),
            change=float(row.get("last_price", 0.0)) - float(row.get("prev_close_price", 0.0)),
            change_percent=float(row.get("change_rate", 0.0)),
            previous_close=float(row.get("prev_close_price", 0.0)),
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
