from __future__ import annotations

from datetime import UTC, datetime

import httpx

from app.schemas.models import NewsItem


class AlphaVantageNewsError(Exception):
    pass


class AlphaVantageRateLimitError(AlphaVantageNewsError):
    pass


class AlphaVantageNewsProvider:
    source_name = "alpha_vantage"

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    async def search(self, tickers: list[str]) -> list[NewsItem]:
        if not self.api_key:
            return []
        ticker_param = ",".join(sorted(set(tickers)))
        async with httpx.AsyncClient(timeout=15.0, trust_env=False) as client:
            response = await client.get(
                "https://www.alphavantage.co/query",
                params={
                    "function": "NEWS_SENTIMENT",
                    "tickers": ticker_param,
                    "apikey": self.api_key,
                    "limit": 25,
                },
            )
            response.raise_for_status()
            payload = response.json()
        if payload.get("Note"):
            raise AlphaVantageRateLimitError(str(payload["Note"]))
        if payload.get("Error Message"):
            raise AlphaVantageNewsError(str(payload["Error Message"]))
        if payload.get("Information"):
            raise AlphaVantageNewsError(str(payload["Information"]))
        items = []
        for entry in payload.get("feed", []):
            published = entry.get("time_published", "19700101T000000")
            published_at = datetime.strptime(published, "%Y%m%dT%H%M%S").replace(tzinfo=UTC)
            score = float(entry.get("overall_sentiment_score", 0.0))
            sentiment = "neutral"
            if score > 0.15:
                sentiment = "positive"
            elif score < -0.15:
                sentiment = "negative"
            items.append(
                NewsItem(
                    id=entry.get("url", entry.get("title", published)),
                    title=entry.get("title", ""),
                    summary=entry.get("summary", ""),
                    url=entry.get("url", ""),
                    source=entry.get("source", "Alpha Vantage"),
                    published_at=published_at,
                    sentiment=sentiment,
                    score=score,
                    matched_symbols=[
                        topic.get("ticker", "") for topic in entry.get("ticker_sentiment", [])
                    ],
                )
            )
        return items
