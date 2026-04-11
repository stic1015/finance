from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/markets/overview")
async def get_market_overview(request: Request):
    market_service = request.app.state.market_service
    repository = request.app.state.repository
    overview = market_service.get_market_overview(repository.list_watchlist())
    # Keep overview fast and deterministic. News is fetched asynchronously by the frontend.
    overview.top_news = []
    return {"data": overview}


@router.get("/markets/briefs")
async def get_market_briefs(request: Request):
    news_service = request.app.state.news_service
    briefs = await news_service.get_market_briefs()
    return {"data": briefs}
