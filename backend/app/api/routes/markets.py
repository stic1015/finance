from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/markets/overview")
async def get_market_overview(request: Request):
    market_service = request.app.state.market_service
    repository = request.app.state.repository
    overview = market_service.get_market_overview(repository.list_watchlist())
    return {"data": overview}
