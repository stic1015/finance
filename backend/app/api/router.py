from fastapi import APIRouter

from app.api.routes import backtests, forecasts, markets, stocks, system

api_router = APIRouter(prefix="/api")
api_router.include_router(markets.router, tags=["markets"])
api_router.include_router(stocks.router, tags=["stocks"])
api_router.include_router(backtests.router, tags=["backtests"])
api_router.include_router(forecasts.router, tags=["forecasts"])
api_router.include_router(system.router, tags=["system"])
