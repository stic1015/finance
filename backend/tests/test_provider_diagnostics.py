import asyncio
import sys
import types
from datetime import UTC, datetime

from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import app
from app.schemas.models import MarketSnapshot, NewsItem, OverviewSection
from app.services.market_data.service import MarketDataService
from app.services.market_data.providers.base import ProviderUnavailableError
from app.services.news.service import NewsService


class _FakeSocket:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


def test_futu_diagnose_reports_fixture_when_sdk_is_missing(monkeypatch):
    settings = Settings(MARKET_PROVIDER="futu", ENABLE_FIXTURE_MODE=True)
    service = MarketDataService(settings)

    original_import = __import__

    def raising_import(name, *args, **kwargs):
        if name == "futu":
            raise ImportError("missing futu")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr("builtins.__import__", raising_import)
    diagnostic = service.diagnose()

    assert diagnostic.provider == "futu"
    assert diagnostic.status == "fixture"
    assert "not installed" in diagnostic.detail


def test_futu_diagnose_reports_fixture_when_opend_is_unreachable(monkeypatch):
    settings = Settings(MARKET_PROVIDER="futu", ENABLE_FIXTURE_MODE=True)
    service = MarketDataService(settings)

    monkeypatch.setitem(sys.modules, "futu", types.ModuleType("futu"))

    def raise_socket_error(*args, **kwargs):
        raise OSError("connection refused")

    monkeypatch.setattr("app.services.market_data.service.socket.create_connection", raise_socket_error)
    diagnostic = service.diagnose()

    assert diagnostic.provider == "futu"
    assert diagnostic.status == "fixture"
    assert "not reachable" in diagnostic.detail


def test_futu_diagnose_reports_live_when_sdk_and_socket_are_ready(monkeypatch):
    settings = Settings(MARKET_PROVIDER="futu", ENABLE_FIXTURE_MODE=True)
    service = MarketDataService(settings)

    monkeypatch.setitem(sys.modules, "futu", types.ModuleType("futu"))
    monkeypatch.setattr(
        "app.services.market_data.service.socket.create_connection",
        lambda *args, **kwargs: _FakeSocket(),
    )

    diagnostic = service.diagnose()

    assert diagnostic.provider == "futu"
    assert diagnostic.status == "live"
    assert "reachable" in diagnostic.detail


def test_news_service_reports_missing_key_and_no_results(monkeypatch):
    missing_key_service = NewsService(Settings(ALPHA_VANTAGE_API_KEY=""))

    async def no_keyword_results(*args, **kwargs):
        return []

    monkeypatch.setattr(missing_key_service.keyword_provider, "search", no_keyword_results)
    missing_key_feed = asyncio.run(missing_key_service.get_news_for_symbol("US.AAPL"))

    assert missing_key_feed.source_status == "unavailable"
    assert missing_key_feed.empty_reason == "missing_api_key"

    live_service = NewsService(Settings(ALPHA_VANTAGE_API_KEY="demo"))

    async def no_results(*args, **kwargs):
        return []

    monkeypatch.setattr(live_service.alpha_provider, "search", no_results)
    monkeypatch.setattr(live_service.keyword_provider, "search", no_keyword_results)
    live_feed = asyncio.run(live_service.get_news_for_symbol("US.AAPL"))

    assert live_feed.source_status == "live"
    assert live_feed.empty_reason == "no_results"


def test_news_service_returns_live_items_when_provider_matches(monkeypatch):
    service = NewsService(Settings(ALPHA_VANTAGE_API_KEY="demo"))

    async def live_results(*args, **kwargs):
        return [
            NewsItem(
                id="1",
                title="AAPL attracts upbeat coverage",
                summary="Provider test payload.",
                url="https://example.com/aapl",
                source="Alpha Vantage",
                published_at="2026-01-01T00:00:00Z",
                sentiment="positive",
                score=0.31,
                matched_symbols=["US.AAPL"],
            )
        ]

    monkeypatch.setattr(service.alpha_provider, "search", live_results)

    async def no_keyword_results(*args, **kwargs):
        return []

    monkeypatch.setattr(service.keyword_provider, "search", no_keyword_results)
    feed = asyncio.run(service.get_news_for_symbol("US.AAPL"))

    assert feed.source_status == "live"
    assert feed.empty_reason is None
    assert len(feed.items) == 1


def test_market_overview_keeps_hk_and_cn_live_when_us_falls_back(monkeypatch):
    settings = Settings(MARKET_PROVIDER="futu", ENABLE_FIXTURE_MODE=True)
    service = MarketDataService(settings)

    def fake_section(region: str):
        if region == "US":
            raise ProviderUnavailableError("permission denied")
        return OverviewSection(region=region, title=f"{region} Session", source_status="live", metrics=[])

    def fake_snapshot(symbol: str):
        if symbol == "US.AAPL":
            raise ProviderUnavailableError("permission denied")
        return MarketSnapshot(
            symbol=symbol,
            display_name=symbol,
            price=100.0,
            change=1.0,
            change_percent=1.0,
            previous_close=99.0,
            open=99.5,
            high=101.0,
            low=98.8,
            volume=1_000_000,
            turnover=90_000_000,
            timestamp=datetime.now(tz=UTC),
            market_state="OPEN",
            source_status="live",
        )

    monkeypatch.setattr(service.primary_provider, "get_overview_section", fake_section)
    monkeypatch.setattr(service.primary_provider, "get_snapshot", fake_snapshot)

    overview = service.get_market_overview(["US.AAPL", "HK.00700", "SH.600519"])

    assert overview.source_status == "delayed"
    assert {section.region: section.source_status for section in overview.sections}["US"] == "fixture"
    assert {section.region: section.source_status for section in overview.sections}["HK"] == "live"
    assert {item.symbol: item.source_status for item in overview.watchlist}["US.AAPL"] == "fixture"
    assert {item.symbol: item.source_status for item in overview.watchlist}["HK.00700"] == "live"


def test_system_health_exposes_runtime_modes():
    with TestClient(app) as client:
        response = client.get("/api/system/health")

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["database_mode"] in {"sqlite", "memory"}
    assert payload["executor_mode"] in {"process_pool", "thread_pool"}
    assert payload["market_provider_status"] in {"live", "fixture", "unavailable", "delayed"}
    assert payload["news_provider_status"] in {"live", "fixture", "unavailable", "delayed"}
