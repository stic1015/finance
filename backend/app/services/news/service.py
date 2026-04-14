from __future__ import annotations

import httpx

from app.core.config import Settings
from app.schemas.models import NewsFeedResponse, NewsItem, ProviderDiagnostic
from app.services.market_data.symbol import aliases_for
from app.services.news.providers.alpha_vantage import (
    AlphaVantageNewsError,
    AlphaVantageNewsProvider,
    AlphaVantageRateLimitError,
)
from app.services.news.providers.keyword import KeywordNewsProvider
from app.services.news.providers.rss import RssNewsProvider


class NewsService:
    sample_symbols = ["US.AAPL", "HK.00700", "SH.600519"]
    sector_topics = {
        "HK.00700": ["Tencent", "Hong Kong internet", "gaming"],
        "HK.09988": ["Alibaba", "Hong Kong internet", "e-commerce"],
        "HK.03690": ["Meituan", "local services", "consumer"],
        "HK.01810": ["Xiaomi", "consumer electronics", "smart devices"],
        "HK.00981": ["SMIC", "semiconductor", "chip"],
        "SH.600519": ["Kweichow Moutai", "consumer", "liquor"],
        "SH.601318": ["Ping An", "insurance", "financials"],
        "SH.600036": ["China Merchants Bank", "bank", "financials"],
        "SZ.300750": ["CATL", "EV battery", "new energy"],
        "SZ.002594": ["BYD", "EV", "automobile"],
        "SZ.000001": ["Ping An Bank", "bank", "financials"],
    }

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.alpha_provider = AlphaVantageNewsProvider(settings.alpha_vantage_api_key)
        self.keyword_provider = KeywordNewsProvider()
        self.rss_provider = RssNewsProvider()

    def diagnose(self) -> ProviderDiagnostic:
        if not self.alpha_provider.api_key:
            return ProviderDiagnostic(
                provider=self.alpha_provider.source_name,
                status="unavailable",
                detail=(
                    "ALPHA_VANTAGE_API_KEY is missing. The API can still return empty-state diagnostics, "
                    "but live attributed headlines are unavailable."
                ),
                sample_symbols=self.sample_symbols,
            )

        return ProviderDiagnostic(
            provider=self.alpha_provider.source_name,
            status="live",
            detail=(
                "Alpha Vantage credentials are configured. The service queries NEWS_SENTIMENT first, "
                "then uses keyword and RSS fallback only when direct attribution is sparse."
            ),
            sample_symbols=self.sample_symbols,
        )

    async def get_news_for_symbol(self, symbol: str) -> NewsFeedResponse:
        aliases = aliases_for(symbol)
        normalized = [alias for alias in aliases if "." in alias and alias.count(".") == 1]

        alpha_items: list[NewsItem] = []
        keyword_items: list[NewsItem] = []
        rss_items: list[NewsItem] = []
        sector_keyword_items: list[NewsItem] = []
        sector_rss_items: list[NewsItem] = []

        source_status = "live"
        feed_type = "stock"
        empty_reason: str | None = None
        message: str | None = None

        try:
            alpha_items = await self.alpha_provider.search(normalized)
        except AlphaVantageRateLimitError:
            source_status = "unavailable"
            empty_reason = "rate_limited"
            message = (
                "Alpha Vantage rate-limited the request. Wait for quota reset or add a higher-capacity provider."
            )
        except (AlphaVantageNewsError, httpx.HTTPError) as exc:
            source_status = "unavailable"
            empty_reason = "provider_unavailable"
            message = f"Alpha Vantage request failed: {exc}"

        keyword_items = await self.keyword_provider.search(aliases, matched_symbols=[symbol])

        # RSS is a supplement source and only used when direct attributed headlines are absent.
        if not alpha_items:
            rss_items = await self.rss_provider.search(aliases, matched_symbols=[symbol])

        if not alpha_items and not keyword_items and not rss_items:
            topics = self.sector_topics_for(symbol)
            sector_keyword_items = await self.keyword_provider.search(topics, matched_symbols=[symbol])
            sector_rss_items = await self.rss_provider.search(topics, matched_symbols=[symbol])

        merged = self._dedupe(alpha_items + keyword_items + rss_items + sector_keyword_items + sector_rss_items)
        sorted_items = sorted(merged, key=lambda item: item.published_at, reverse=True)

        providers: list[str] = []
        if alpha_items:
            providers.append(self.alpha_provider.source_name)
        if keyword_items or sector_keyword_items:
            providers.append(self.keyword_provider.source_name)
        if rss_items or sector_rss_items:
            providers.append(self.rss_provider.source_name)

        provider = "+".join(providers) if providers else self.alpha_provider.source_name

        if alpha_items and (keyword_items or rss_items):
            source_status = "live"
            feed_type = "mixed"
            message = "Direct attributed headlines were supplemented with keyword/RSS backfill coverage."
        elif alpha_items:
            source_status = "live"
            feed_type = "stock"
            message = "Live attributed headlines are available from Alpha Vantage."
        elif keyword_items or rss_items:
            source_status = "delayed"
            feed_type = "stock"
            empty_reason = "keyword_or_rss_only"
            message = "No directly attributed headlines found. Showing keyword/RSS fallback coverage."
        elif sector_keyword_items or sector_rss_items:
            source_status = "delayed"
            feed_type = "sector"
            empty_reason = "sector_only"
            message = "No stock-specific headlines found. Showing sector-level briefs instead."
        elif not self.alpha_provider.api_key:
            source_status = "unavailable"
            empty_reason = "missing_api_key"
            message = (
                "Add ALPHA_VANTAGE_API_KEY to enable attributed headlines. "
                "Without it, the feed stays in diagnostics-only mode."
            )
        elif empty_reason is None:
            source_status = "live"
            empty_reason = "no_results"
            message = "Live provider responded successfully, but no attributable headlines matched this symbol."

        return NewsFeedResponse(
            symbol=symbol,
            provider=provider,
            source_status=source_status,
            feed_type=feed_type,
            items=sorted_items,
            empty_reason=empty_reason,
            message=message,
        )

    async def get_market_briefs(self) -> NewsFeedResponse:
        topics = ["Hong Kong stocks", "A-shares", "semiconductor", "new energy vehicles", "financials"]
        keyword_items = await self.keyword_provider.search(topics, matched_symbols=["HK", "CN"])
        rss_items = await self.rss_provider.search(topics, matched_symbols=["HK", "CN"])
        merged = self._dedupe(keyword_items + rss_items)
        items = sorted(merged, key=lambda item: item.published_at, reverse=True)

        providers: list[str] = []
        if keyword_items:
            providers.append(self.keyword_provider.source_name)
        if rss_items:
            providers.append(self.rss_provider.source_name)
        provider = "+".join(providers) if providers else "none"

        return NewsFeedResponse(
            symbol="MARKET",
            provider=provider,
            source_status="delayed" if items else "unavailable",
            feed_type="sector",
            items=items,
            empty_reason=None if items else "no_results",
            message="Industry and market briefs." if items else "No market briefs available.",
        )

    def sector_topics_for(self, symbol: str) -> list[str]:
        return self.sector_topics.get(symbol, aliases_for(symbol))

    def _dedupe(self, items: list[NewsItem]) -> list[NewsItem]:
        seen: set[str] = set()
        unique: list[NewsItem] = []
        for item in items:
            key = (item.url or item.title).strip().lower()
            if not key or key in seen:
                continue
            seen.add(key)
            unique.append(item)
        return unique
