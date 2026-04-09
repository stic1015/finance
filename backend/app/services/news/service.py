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


class NewsService:
    sample_symbols = ["US.AAPL", "HK.00700", "SH.600519"]
    sector_topics = {
        "HK.00700": ["腾讯", "港股互联网", "游戏"],
        "HK.09988": ["阿里巴巴", "港股互联网", "电商"],
        "HK.03690": ["美团", "本地生活", "消费"],
        "HK.01810": ["小米", "消费电子", "智能硬件"],
        "HK.00981": ["中芯国际", "半导体", "芯片"],
        "SH.600519": ["白酒", "消费", "贵州茅台"],
        "SH.601318": ["保险", "金融", "中国平安"],
        "SH.600036": ["银行", "金融", "招商银行"],
        "SZ.300750": ["新能源车", "动力电池", "宁德时代"],
        "SZ.002594": ["新能源车", "比亚迪", "整车"],
        "SZ.000001": ["银行", "金融", "平安银行"],
    }

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.alpha_provider = AlphaVantageNewsProvider(settings.alpha_vantage_api_key)
        self.keyword_provider = KeywordNewsProvider()

    def diagnose(self) -> ProviderDiagnostic:
        if not self.alpha_provider.api_key:
            return ProviderDiagnostic(
                provider=self.alpha_provider.source_name,
                status="unavailable",
                detail=(
                    "ALPHA_VANTAGE_API_KEY is missing. The API can still surface empty-state diagnostics, "
                    "but it cannot fetch live attributed headlines."
                ),
                sample_symbols=self.sample_symbols,
            )

        return ProviderDiagnostic(
            provider=self.alpha_provider.source_name,
            status="live",
            detail=(
                "Alpha Vantage credentials are configured. The service will query NEWS_SENTIMENT first "
                "and then use alias-based keyword backfill when direct attribution is sparse."
            ),
            sample_symbols=self.sample_symbols,
        )

    async def get_news_for_symbol(self, symbol: str) -> NewsFeedResponse:
        aliases = aliases_for(symbol)
        normalized = [alias for alias in aliases if "." in alias and alias.count(".") == 1]
        alpha_items = []
        keyword_items = []
        sector_items = []
        provider = self.alpha_provider.source_name
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
                "Alpha Vantage rate-limited the request. Wait for the quota window to reset, "
                "or add a higher-capacity news provider."
            )
        except (AlphaVantageNewsError, httpx.HTTPError) as exc:
            source_status = "unavailable"
            empty_reason = "provider_unavailable"
            message = f"Alpha Vantage request failed: {exc}"

        keyword_items = await self.keyword_provider.search(aliases, matched_symbols=[symbol])
        if not alpha_items and not keyword_items:
            sector_items = await self.keyword_provider.search(self.sector_topics_for(symbol), matched_symbols=[symbol])
        merged = self._dedupe(alpha_items + keyword_items + sector_items)
        sorted_items = sorted(merged, key=lambda item: item.published_at, reverse=True)

        if alpha_items and keyword_items:
            provider = f"{self.alpha_provider.source_name}+{self.keyword_provider.source_name}"
            source_status = "live"
            feed_type = "mixed"
            message = "Direct attributed headlines were enriched with alias-based keyword backfill."
        elif alpha_items:
            provider = self.alpha_provider.source_name
            source_status = "live"
            feed_type = "stock"
            message = "Live attributed headlines are available from Alpha Vantage."
        elif keyword_items:
            provider = self.keyword_provider.source_name
            source_status = "delayed"
            feed_type = "stock"
            empty_reason = "keyword_only"
            message = "No directly attributed headlines were found. Showing alias-based fallback coverage."
        elif sector_items:
            provider = self.keyword_provider.source_name
            source_status = "delayed"
            feed_type = "sector"
            empty_reason = "sector_only"
            message = "No stock-specific headlines were found. Showing sector briefs instead."
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
            message = "The live provider responded successfully, but no attributable headlines matched this symbol."

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
        items = await self.keyword_provider.search(
            ["港股", "A股", "半导体", "新能源车", "金融"],
            matched_symbols=["HK", "CN"],
        )
        return NewsFeedResponse(
            symbol="MARKET",
            provider=self.keyword_provider.source_name if items else "none",
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
            key = item.url or item.title.lower()
            if key in seen:
                continue
            seen.add(key)
            unique.append(item)
        return unique
