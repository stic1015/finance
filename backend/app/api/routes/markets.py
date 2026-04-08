from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/markets/overview")
async def get_market_overview(request: Request):
    market_service = request.app.state.market_service
    repository = request.app.state.repository
    overview = market_service.get_market_overview(repository.list_watchlist())
    news_service = request.app.state.news_service
    top_news = []
    seen: set[str] = set()
    for symbol in repository.list_watchlist():
        feed = await news_service.get_news_for_symbol(symbol)
        for item in feed.items:
            key = item.url or item.id
            if key in seen:
                continue
            seen.add(key)
            top_news.append(item)
    overview.top_news = sorted(top_news, key=lambda item: item.published_at, reverse=True)[:6]
    return {"data": overview}
