from fastapi import APIRouter, HTTPException, Request

from app.schemas.models import BacktestRequest

router = APIRouter()


@router.post("/backtests")
async def create_backtest_job(payload: BacktestRequest, request: Request):
    market_service = request.app.state.market_service
    candles = market_service.get_candles(payload.symbol, interval=payload.interval, limit=420)
    job = request.app.state.backtest_jobs.submit(payload, [point.model_dump() for point in candles.points])
    return {"data": job}


@router.get("/backtests/{job_id}")
async def get_backtest_job(job_id: str, request: Request):
    job = request.app.state.backtest_jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Backtest job not found.")
    return {"data": job}
