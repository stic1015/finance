from __future__ import annotations

from datetime import UTC, datetime, timedelta
from hashlib import sha256
from random import Random

from app.schemas.models import (
    CandlePoint,
    CandleSeries,
    MarketMetric,
    MarketOverview,
    MarketSnapshot,
    NewsItem,
    OverviewSection,
)
from app.services.market_data.symbol import display_name_for, to_futu_code

from .base import MarketDataProvider


INDEX_MAP = {
    "US": [("US.SPY", "标普500"), ("US.QQQ", "纳指100"), ("US.DIA", "道琼斯")],
    "HK": [("HK.800000", "恒生指数"), ("HK.800700", "恒生科技"), ("HK.800100", "国企指数")],
    "CN": [("SH.000001", "上证综指"), ("SZ.399001", "深证成指"), ("SZ.399006", "创业板指")],
}


def seeded_rng(symbol: str) -> Random:
    seed = int(sha256(symbol.encode("utf-8")).hexdigest()[:16], 16)
    return Random(seed)


class FixtureMarketDataProvider(MarketDataProvider):
    source_name = "fixture"

    def get_overview_section(self, region: str) -> OverviewSection:
        metrics = INDEX_MAP[region]
        section_metrics = []
        for symbol, label in metrics:
            rng = seeded_rng(symbol)
            value = round(rng.uniform(90, 300) * (100 if region != "US" else 20), 2)
            change_pct = round(rng.uniform(-2.5, 2.5), 2)
            section_metrics.append(
                MarketMetric(label=label, value=value, change_percent=change_pct, symbol=symbol)
            )
        return OverviewSection(
            region=region,
            title={"US": "美股时段", "HK": "港股时段", "CN": "A股时段"}[region],
            source_status="fixture",
            metrics=section_metrics,
        )

    def get_market_overview(self, watchlist: list[str]) -> MarketOverview:
        sections = [self.get_overview_section(region) for region in INDEX_MAP]

        top_news = [
            NewsItem(
                id="fixture-1",
                title="Macro liquidity cools while AI capex remains resilient",
                summary="Fixture news for UI verification. Replace with Alpha Vantage or keyword adapters.",
                url="https://example.com/fixture-news-1",
                source="Fixture Wire",
                published_at=datetime.now(tz=UTC) - timedelta(minutes=18),
                sentiment="neutral",
                score=0.11,
                matched_symbols=["US.NVDA", "US.MSFT"],
            ),
            NewsItem(
                id="fixture-2",
                title="Consumer and platform names diverge across Asia session",
                summary="Fixture news keeps the overview feed usable before credentials are added.",
                url="https://example.com/fixture-news-2",
                source="Fixture Wire",
                published_at=datetime.now(tz=UTC) - timedelta(minutes=42),
                sentiment="positive",
                score=0.41,
                matched_symbols=["HK.00700", "SZ.300750"],
            ),
        ]

        snapshots = [self.get_snapshot(symbol) for symbol in watchlist]
        return MarketOverview(
            generated_at=datetime.now(tz=UTC),
            provider=self.source_name,
            source_status="fixture",
            sections=sections,
            top_news=top_news,
            watchlist=snapshots,
        )

    def get_snapshot(self, symbol: str) -> MarketSnapshot:
        normalized = to_futu_code(symbol)
        rng = seeded_rng(normalized)
        previous_close = round(rng.uniform(40, 500), 2)
        move = round(rng.uniform(-0.05, 0.05) * previous_close, 2)
        price = round(previous_close + move, 2)
        high = round(max(price, previous_close) + abs(rng.uniform(0.1, 0.03) * previous_close), 2)
        low = round(min(price, previous_close) - abs(rng.uniform(0.1, 0.03) * previous_close), 2)
        return MarketSnapshot(
            symbol=normalized,
            display_name=display_name_for(normalized),
            price=price,
            change=round(price - previous_close, 2),
            change_percent=round((price - previous_close) / previous_close * 100, 2),
            previous_close=previous_close,
            open=round(previous_close + rng.uniform(-0.02, 0.02) * previous_close, 2),
            high=max(high, price),
            low=min(low, price),
            volume=round(rng.uniform(1_000_000, 30_000_000), 0),
            turnover=round(rng.uniform(50_000_000, 500_000_000), 0),
            timestamp=datetime.now(tz=UTC),
            market_state="SIMULATED",
            source_status="fixture",
        )

    def get_candles(self, symbol: str, interval: str = "1d", limit: int = 180) -> CandleSeries:
        normalized = to_futu_code(symbol)
        rng = seeded_rng(normalized)
        base = round(rng.uniform(50, 350), 2)
        points: list[CandlePoint] = []
        current = base
        now = datetime.now(tz=UTC)
        for index in range(limit):
            timestamp = now - timedelta(days=limit - index)
            drift = rng.uniform(-0.025, 0.03)
            open_price = current
            close_price = max(1.0, open_price * (1 + drift))
            high = max(open_price, close_price) * (1 + rng.uniform(0.001, 0.02))
            low = min(open_price, close_price) * (1 - rng.uniform(0.001, 0.02))
            volume = rng.uniform(800_000, 20_000_000)
            points.append(
                CandlePoint(
                    timestamp=timestamp,
                    open=round(open_price, 2),
                    high=round(high, 2),
                    low=round(low, 2),
                    close=round(close_price, 2),
                    volume=round(volume, 0),
                )
            )
            current = close_price
        return CandleSeries(symbol=normalized, interval=interval, source_status="fixture", points=points)
