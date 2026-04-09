from __future__ import annotations

from datetime import UTC, datetime
from urllib.parse import quote
from xml.etree import ElementTree

import httpx

from app.schemas.models import NewsItem


class KeywordNewsProvider:
    source_name = "keyword"

    async def search(self, aliases: list[str]) -> list[NewsItem]:
        if not aliases:
            return []

        query_terms = [alias for alias in aliases if alias and "." not in alias][:2]
        if not query_terms:
            return []

        query = " OR ".join(f'"{term}"' for term in query_terms)
        url = f"https://news.google.com/rss/search?q={quote(query)}&hl=zh-CN&gl=CN&ceid=CN:zh-Hans"
        try:
            async with httpx.AsyncClient(timeout=10.0, trust_env=False) as client:
                response = await client.get(url)
                response.raise_for_status()
        except httpx.HTTPError:
            return []

        root = ElementTree.fromstring(response.text)
        items: list[NewsItem] = []
        for item in root.findall(".//item")[:8]:
            title = item.findtext("title", default="")
            link = item.findtext("link", default="")
            pub_date = item.findtext("pubDate", default="")
            source = item.findtext("source", default="Google News RSS")
            published_at = datetime.now(tz=UTC)
            if pub_date:
                try:
                    published_at = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %Z").replace(tzinfo=UTC)
                except ValueError:
                    published_at = datetime.now(tz=UTC)
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
                    matched_symbols=aliases,
                )
            )
        return items
