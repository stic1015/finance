from __future__ import annotations

import asyncio
from datetime import UTC, datetime

from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import app
from app.schemas.models import MarketSnapshot
from app.services.market_data.service import MarketDataService
from app.services.news.service import NewsService
from app.services.opportunity.service import OpportunityService, _OpportunityCandidate
from app.storage.repositories import MemoryRepository


def _snapshot(symbol: str, source_status: str = "live") -> MarketSnapshot:
    return MarketSnapshot(
        symbol=symbol,
        display_name=symbol,
        price=100.0,
        change=1.2,
        change_percent=1.2,
        previous_close=98.8,
        open=99.0,
        high=101.0,
        low=97.5,
        volume=2_000_000,
        turnover=200_000_000,
        timestamp=datetime.now(tz=UTC),
        market_state="OPEN",
        source_status=source_status,  # type: ignore[arg-type]
    )


def _candidate(symbol: str, score: float, risk_score: float, source_status: str = "live") -> _OpportunityCandidate:
    return _OpportunityCandidate(
        snapshot=_snapshot(symbol, source_status=source_status),
        score=score,
        risk_score=risk_score,
        reasons=["test"],
    )


def test_classification_thresholds_for_buy_watch_avoid():
    service = OpportunityService(
        Settings(MARKET_PROVIDER="fixture"),
        MarketDataService(Settings(MARKET_PROVIDER="fixture")),
        NewsService(Settings(ALPHA_VANTAGE_API_KEY="demo")),
        MemoryRepository(),
    )
    items = service._classify_candidates(  # type: ignore[attr-defined]
        [
            _candidate("HK.00700", 78.0, 20.0),
            _candidate("SH.600519", 74.0, 35.0),
            _candidate("SZ.300750", 44.0, 30.0),
        ]
    )
    assert items[0].action == "buy"
    assert any(item.action == "watch" for item in items)
    assert any(item.action == "avoid" for item in items)


def test_opportunity_response_has_expected_shape(monkeypatch):
    settings = Settings(MARKET_PROVIDER="fixture")
    service = OpportunityService(
        settings,
        MarketDataService(settings),
        NewsService(Settings(ALPHA_VANTAGE_API_KEY="demo")),
        MemoryRepository(),
    )

    async def no_news(_candidates):
        return None

    monkeypatch.setattr(service, "_enrich_news_signal", no_news)  # type: ignore[arg-type]
    response = asyncio.run(service.get_opportunities(["HK", "CN"], limit=20))

    assert response.refresh_interval_sec == 300
    assert response.universe_size >= response.scanned_size
    assert len(response.items) <= 20
    assert response.source_status in {"live", "delayed", "unavailable"}
    assert response.items


def test_markets_opportunities_api_route_returns_new_schema(monkeypatch):
    with TestClient(app) as client:
        service = client.app.state.opportunity_service

        async def no_news(_candidates):
            return None

        monkeypatch.setattr(service, "_enrich_news_signal", no_news)  # type: ignore[arg-type]
        response = client.get("/api/markets/opportunities?markets=HK,CN&limit=15")

    assert response.status_code == 200
    payload = response.json()["data"]
    assert "generated_at" in payload
    assert payload["refresh_interval_sec"] == 300
    assert "universe_size" in payload
    assert "scanned_size" in payload
    assert isinstance(payload["items"], list)
    if payload["items"]:
        item = payload["items"][0]
        assert {"symbol", "display_name", "price", "change_percent", "action", "score", "risk_score", "reasons"} <= set(
            item.keys()
        )
