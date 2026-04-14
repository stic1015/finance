from __future__ import annotations

import sys
import types
from datetime import UTC, datetime

import pandas as pd

from app.core.config import Settings
from app.schemas.models import MarketOverview, MarketSnapshot, OverviewSection
from app.services.market_data.providers.futu import FutuMarketDataProvider
from app.services.market_data.service import MarketDataService


class _FakeQuoteContext:
    def __init__(self, tracker: dict[str, object]) -> None:
        self.tracker = tracker

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def subscribe(self, symbols, sub_types, subscribe_push=False):
        self.tracker["sub_types"] = sub_types
        return 0, {}

    def get_cur_kline(self, symbol, num, ktype, autype):
        self.tracker["ktype"] = ktype
        frame = pd.DataFrame(
            [
                {
                    "time_key": "2026-01-01 09:30:00",
                    "open": 100.0,
                    "high": 101.0,
                    "low": 99.0,
                    "close": 100.5,
                    "volume": 1000000,
                }
            ]
        )
        return 0, frame


def test_futu_provider_maps_30m_interval(monkeypatch):
    tracker: dict[str, object] = {}
    provider = FutuMarketDataProvider("127.0.0.1", 11111, Settings().futu_sdk_appdata_path)
    monkeypatch.setattr(provider, "_get_context", lambda: _FakeQuoteContext(tracker))

    fake_futu = types.SimpleNamespace(
        AuType=types.SimpleNamespace(QFQ="QFQ"),
        KLType=types.SimpleNamespace(K_DAY="K_DAY", K_60M="K_60M", K_30M="K_30M", K_15M="K_15M"),
        SubType=types.SimpleNamespace(K_DAY="K_DAY", K_60M="K_60M", K_30M="K_30M", K_15M="K_15M"),
    )
    monkeypatch.setitem(sys.modules, "futu", fake_futu)

    series = provider.get_candles("HK.00700", interval="30m", limit=1)

    assert series.interval == "30m"
    assert tracker["ktype"] == "K_30M"
    assert tracker["sub_types"] == ["K_30M"]


def test_snapshot_change_percent_fallback_when_provider_value_is_missing():
    service = MarketDataService(Settings(MARKET_PROVIDER="fixture"))
    service.primary_provider.get_snapshot = lambda symbol: MarketSnapshot(  # type: ignore[method-assign]
        symbol=symbol,
        display_name=symbol,
        price=110.0,
        change=10.0,
        change_percent=0.0,
        previous_close=100.0,
        open=101.0,
        high=112.0,
        low=99.0,
        volume=1_000_000,
        turnover=100_000_000,
        timestamp=datetime.now(tz=UTC),
        market_state="OPEN",
        source_status="live",
    )

    snapshot = service.get_snapshot("HK.00700")
    assert round(snapshot.change_percent, 2) == 10.0


def test_snapshot_change_percent_is_zero_when_previous_close_not_positive():
    service = MarketDataService(Settings(MARKET_PROVIDER="fixture"))
    service.primary_provider.get_snapshot = lambda symbol: MarketSnapshot(  # type: ignore[method-assign]
        symbol=symbol,
        display_name=symbol,
        price=110.0,
        change=10.0,
        change_percent=0.0,
        previous_close=0.0,
        open=101.0,
        high=112.0,
        low=99.0,
        volume=1_000_000,
        turnover=100_000_000,
        timestamp=datetime.now(tz=UTC),
        market_state="OPEN",
        source_status="live",
    )

    snapshot = service.get_snapshot("HK.00700")
    assert snapshot.change_percent == 0.0


def test_market_overview_normalizes_watchlist_change_percent():
    service = MarketDataService(Settings(MARKET_PROVIDER="fixture"))
    service.primary_provider.get_market_overview = lambda watchlist: MarketOverview(  # type: ignore[method-assign]
        generated_at=datetime.now(tz=UTC),
        provider="fixture",
        source_status="live",
        sections=[OverviewSection(region="HK", title="HK Session", source_status="live", metrics=[])],
        top_news=[],
        watchlist=[
            MarketSnapshot(
                symbol="HK.00700",
                display_name="HK.00700",
                price=105.0,
                change=5.0,
                change_percent=0.0,
                previous_close=100.0,
                open=100.0,
                high=106.0,
                low=99.0,
                volume=1_000_000,
                turnover=100_000_000,
                timestamp=datetime.now(tz=UTC),
                market_state="OPEN",
                source_status="live",
            )
        ],
    )

    overview = service.get_market_overview(["HK.00700"])
    assert round(overview.watchlist[0].change_percent, 2) == 5.0
