from fastapi import APIRouter, Query, Request

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


@router.get("/markets/opportunities")
async def get_market_opportunities(
    request: Request,
    markets: str = Query(default="HK,CN"),
    limit: int = Query(default=50, ge=10, le=200),
):
    opportunity_service = request.app.state.opportunity_service
    market_list = [token.strip().upper() for token in markets.split(",") if token.strip()]
    opportunities = await opportunity_service.get_opportunities(market_list, limit=limit)
    return {"data": opportunities}
