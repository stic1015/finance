import asyncio

from fastapi import APIRouter, Query, Request, WebSocket

router = APIRouter()


@router.get("/stocks/{symbol}/snapshot")
async def get_stock_snapshot(symbol: str, request: Request):
    snapshot = request.app.state.market_service.get_snapshot(symbol)
    return {"data": snapshot}


@router.get("/stocks/{symbol}/candles")
async def get_stock_candles(
    symbol: str,
    request: Request,
    interval: str = Query(default="1d"),
    limit: int = Query(default=180, ge=30, le=1000),
):
    candles = request.app.state.market_service.get_candles(symbol, interval=interval, limit=limit)
    return {"data": candles}


@router.get("/stocks/{symbol}/news")
async def get_stock_news(symbol: str, request: Request):
    news_feed = await request.app.state.news_service.get_news_for_symbol(symbol)
    return {"data": news_feed}


@router.websocket("/ws/stocks/{symbol}")
async def stock_stream(websocket: WebSocket, symbol: str):
    await websocket.accept()
    market_service = websocket.app.state.market_service
    try:
        while True:
            snapshot = market_service.get_snapshot(symbol)
            await websocket.send_json(snapshot.model_dump(mode="json"))
            await asyncio.sleep(5)
    finally:
        await websocket.close()
