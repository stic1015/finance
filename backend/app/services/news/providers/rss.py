from __future__ import annotations

from datetime import UTC, datetime
from urllib.parse import quote
from xml.etree import ElementTree

import httpx

from app.schemas.models import NewsItem


class RssNewsProvider:
    source_name = "rss"

    def __init__(self) -> None:
        self.base_feeds = [
            "https://feeds.reuters.com/reuters/businessNews",
            "https://feeds.marketwatch.com/marketwatch/topstories/",
        ]

    async def search(self, terms: list[str], matched_symbols: list[str] | None = None, limit: int = 8) -> list[NewsItem]:
        if not terms:
            return []

        query_terms = [term for term in terms if term and "." not in term][:4]
        if not query_terms:
            return []

        query = " OR ".join(f'"{term}"' for term in query_terms)
        urls = [
            f"https://news.google.com/rss/search?q={quote(query)}&hl=en-US&gl=US&ceid=US:en",
            *self.base_feeds,
        ]

        items: list[NewsItem] = []
        for url in urls:
            try:
                async with httpx.AsyncClient(timeout=10.0, trust_env=False) as client:
                    response = await client.get(url)
                    response.raise_for_status()
            except httpx.HTTPError:
                continue

            try:
                root = ElementTree.fromstring(response.text)
            except ElementTree.ParseError:
                continue

            for item in root.findall(".//item"):
                title = item.findtext("title", default="")
                link = item.findtext("link", default="")
                pub_date = item.findtext("pubDate", default="")
                source = item.findtext("source", default="RSS")
                if not title and not link:
                    continue

                published_at = datetime.now(tz=UTC)
                if pub_date:
                    for fmt in ("%a, %d %b %Y %H:%M:%S %Z", "%a, %d %b %Y %H:%M:%S %z"):
                        try:
                            parsed = datetime.strptime(pub_date, fmt)
                            published_at = parsed.replace(tzinfo=UTC) if parsed.tzinfo is None else parsed.astimezone(UTC)
                            break
                        except ValueError:
                            continue

                items.append(
                    NewsItem(
                        id=link or title,
                        title=title,
                        summary=title,
                        url=link,
                        source=source,
                        published_at=published_at,
                        sentiment="neutral",
                        score=0.0,
                        matched_symbols=matched_symbols or terms,
                    )
                )
                if len(items) >= limit:
                    return items

        return items
