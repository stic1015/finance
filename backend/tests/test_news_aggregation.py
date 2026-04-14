from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta

from app.core.config import Settings
from app.schemas.models import NewsItem
from app.services.news.service import NewsService


def _item(id_value: str, title: str, minutes_ago: int, url: str) -> NewsItem:
    return NewsItem(
        id=id_value,
        title=title,
        summary=title,
        url=url,
        source="Test",
        published_at=datetime.now(tz=UTC) - timedelta(minutes=minutes_ago),
        sentiment="neutral",
        score=0.0,
        matched_symbols=["US.AAPL"],
    )


def test_news_service_keeps_alpha_priority_and_merges_keyword():
    service = NewsService(Settings(ALPHA_VANTAGE_API_KEY="demo"))

    async def alpha_results(*args, **kwargs):
        return [_item("a", "alpha", 5, "https://example.com/a")]

    async def keyword_results(*args, **kwargs):
        return [_item("k", "keyword", 10, "https://example.com/k")]

    async def rss_results(*args, **kwargs):
        return [_item("r", "rss", 15, "https://example.com/r")]

    service.alpha_provider.search = alpha_results  # type: ignore[method-assign]
    service.keyword_provider.search = keyword_results  # type: ignore[method-assign]
    service.rss_provider.search = rss_results  # type: ignore[method-assign]

    feed = asyncio.run(service.get_news_for_symbol("US.AAPL"))

    assert feed.provider == "alpha_vantage+keyword"
    assert feed.source_status == "live"
    assert feed.feed_type == "mixed"
    assert [item.title for item in feed.items] == ["alpha", "keyword"]


def test_news_service_uses_keyword_and_rss_fallback_with_dedup_and_sort():
    service = NewsService(Settings(ALPHA_VANTAGE_API_KEY="demo"))

    async def no_alpha(*args, **kwargs):
        return []

    async def keyword_results(*args, **kwargs):
        return [
            _item("newer", "newer", 1, "https://example.com/shared"),
            _item("older", "older", 30, "https://example.com/older"),
        ]

    async def rss_results(*args, **kwargs):
        return [
            _item("dup", "duplicate", 2, "https://example.com/shared"),
            _item("mid", "mid", 10, "https://example.com/mid"),
        ]

    service.alpha_provider.search = no_alpha  # type: ignore[method-assign]
    service.keyword_provider.search = keyword_results  # type: ignore[method-assign]
    service.rss_provider.search = rss_results  # type: ignore[method-assign]

    feed = asyncio.run(service.get_news_for_symbol("US.AAPL"))

    assert feed.provider == "keyword+rss"
    assert feed.source_status == "delayed"
    assert feed.feed_type == "stock"
    assert [item.title for item in feed.items] == ["newer", "mid", "older"]


def test_market_briefs_provider_can_be_composite():
    service = NewsService(Settings(ALPHA_VANTAGE_API_KEY="demo"))

    async def keyword_results(*args, **kwargs):
        return [_item("k", "keyword", 20, "https://example.com/k")]

    async def rss_results(*args, **kwargs):
        return [_item("r", "rss", 5, "https://example.com/r")]

    service.keyword_provider.search = keyword_results  # type: ignore[method-assign]
    service.rss_provider.search = rss_results  # type: ignore[method-assign]

    feed = asyncio.run(service.get_market_briefs())

    assert feed.provider == "keyword+rss"
    assert feed.source_status == "delayed"
    assert [item.title for item in feed.items] == ["rss", "keyword"]
