from __future__ import annotations

from app.schemas.models import NewsItem


class KeywordNewsProvider:
    source_name = "keyword"

    async def search(self, aliases: list[str]) -> list[NewsItem]:
        return []
