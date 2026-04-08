from __future__ import annotations

import sqlite3
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import get_settings
from app.services.backtest.jobs import BacktestJobService
from app.services.forecast.service import ForecastService
from app.services.market_data.service import MarketDataService
from app.services.news.service import NewsService
from app.storage.repositories import MemoryRepository, SQLiteRepository
from app.tasks.scheduler import build_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    database_warning = ""
    database_path = settings.sqlite_path
    try:
        repository = SQLiteRepository(database_path)
    except sqlite3.OperationalError:
        database_path = Path("memory://finance-quant-lab")
        database_warning = (
            f"Primary SQLite path {settings.sqlite_path} was unavailable; using in-memory repository."
        )
        repository = MemoryRepository()
    scheduler = build_scheduler()
    market_service = MarketDataService(settings)
    news_service = NewsService(settings)
    backtest_jobs = BacktestJobService(repository)
    app.state.settings = settings
    app.state.repository = repository
    app.state.database_path = database_path
    app.state.database_warning = database_warning
    app.state.market_service = market_service
    app.state.news_service = news_service
    app.state.forecast_service = ForecastService(repository)
    app.state.backtest_jobs = backtest_jobs
    app.state.startup_checks = {
        "market": market_service.diagnose().model_dump(mode="json"),
        "news": news_service.diagnose().model_dump(mode="json"),
    }
    app.state.scheduler = scheduler
    scheduler.start()
    try:
        yield
    finally:
        scheduler.shutdown(wait=False)


app = FastAPI(title="Finance Quant Lab API", version="0.1.0", lifespan=lifespan)
settings = get_settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)
app.include_router(api_router)


@app.get("/")
async def root():
    return {
        "name": "Finance Quant Lab API",
        "version": "0.1.0",
        "docs": "/docs",
    }
