from fastapi import APIRouter, HTTPException, Request

from app.schemas.models import ForecastRequest
from app.services.market_data.symbol import to_futu_code

router = APIRouter()


@router.post("/forecasts/5d")
async def generate_forecast(payload: ForecastRequest, request: Request):
    market_service = request.app.state.market_service
    candles = market_service.get_candles(payload.symbol, interval=payload.interval, limit=payload.lookback)
    result = request.app.state.forecast_service.generate(
        payload,
        [point.model_dump() for point in candles.points],
        candles.source_status,
    )
    return {"data": result}


@router.get("/forecasts/{symbol}")
async def get_latest_forecast(symbol: str, request: Request):
    normalized = to_futu_code(symbol)
    result = request.app.state.forecast_service.latest(normalized)
    if not result:
        raise HTTPException(status_code=404, detail="No cached forecast found for this symbol.")
    return {"data": result}
