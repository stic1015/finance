from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


SourceStatus = Literal["live", "delayed", "fixture", "unavailable"]
DatabaseMode = Literal["sqlite", "memory"]
ExecutorMode = Literal["process_pool", "thread_pool"]
StrategyName = Literal[
    "moving_average_trend",
    "rsi_bollinger_mean_reversion",
    "donchian_volume_breakout",
    "macd_trend_confirmation",
]


class SymbolRef(BaseModel):
    raw: str
    normalized: str
    market: Literal["US", "HK", "SH", "SZ"]
    ticker: str
    display_name: str
    aliases: list[str] = Field(default_factory=list)


class MarketMetric(BaseModel):
    label: str
    value: float
    change_percent: float
    symbol: str


class NewsItem(BaseModel):
    id: str
    title: str
    summary: str
    url: str
    source: str
    published_at: datetime
    sentiment: Literal["positive", "neutral", "negative"]
    score: float = 0.0
    matched_symbols: list[str] = Field(default_factory=list)


class ProviderDiagnostic(BaseModel):
    provider: str
    status: SourceStatus
    detail: str
    sample_symbols: list[str] = Field(default_factory=list)


class NewsFeedResponse(BaseModel):
    symbol: str
    provider: str
    source_status: SourceStatus
    items: list[NewsItem] = Field(default_factory=list)
    empty_reason: str | None = None
    message: str | None = None


class CandlePoint(BaseModel):
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


class CandleSeries(BaseModel):
    symbol: str
    interval: str
    source_status: SourceStatus
    points: list[CandlePoint]


class MarketSnapshot(BaseModel):
    symbol: str
    display_name: str
    price: float
    change: float
    change_percent: float
    previous_close: float
    open: float
    high: float
    low: float
    volume: float
    turnover: float
    timestamp: datetime
    market_state: str
    source_status: SourceStatus


class OverviewSection(BaseModel):
    region: Literal["US", "HK", "CN"]
    title: str
    metrics: list[MarketMetric]


class MarketOverview(BaseModel):
    generated_at: datetime
    provider: str
    source_status: SourceStatus
    sections: list[OverviewSection]
    top_news: list[NewsItem]
    watchlist: list[MarketSnapshot]


class StrategyDefinition(BaseModel):
    name: StrategyName
    label: str
    description: str
    default_params: dict[str, float | int]


class BacktestRequest(BaseModel):
    symbol: str
    strategy: StrategyName
    start_date: datetime
    end_date: datetime
    benchmark_symbol: str = "SPY"
    interval: str = "1d"
    initial_capital: float = 100000.0
    fee_bps: float = 10.0
    slippage_bps: float = 5.0
    params: dict[str, float | int] = Field(default_factory=dict)


class BacktestMetrics(BaseModel):
    cumulative_return: float
    annualized_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    trade_count: int
    benchmark_return: float


class EquityPoint(BaseModel):
    timestamp: datetime
    equity: float
    benchmark_equity: float


class BacktestResult(BaseModel):
    job_id: str
    symbol: str
    strategy: StrategyName
    benchmark_symbol: str
    started_at: datetime
    completed_at: datetime | None = None
    status: Literal["queued", "running", "completed", "failed"]
    metrics: BacktestMetrics | None = None
    equity_curve: list[EquityPoint] = Field(default_factory=list)
    params: dict[str, float | int] = Field(default_factory=dict)
    caveats: list[str] = Field(default_factory=list)
    error: str | None = None


class ForecastScenario(BaseModel):
    label: Literal["bullish", "neutral", "bearish"]
    probability: float
    expected_return: float


class Forecast5DResult(BaseModel):
    symbol: str
    generated_at: datetime
    horizon_days: int = 5
    model_family: str
    source_status: SourceStatus
    expected_return_range: tuple[float, float]
    expected_price_range: tuple[float, float]
    scenarios: list[ForecastScenario]
    rationale: list[str]
    caveat: str


class ForecastRequest(BaseModel):
    symbol: str
    interval: str = "1d"
    lookback: int = 260


class ApiEnvelope(BaseModel):
    data: Any


class HealthResponse(BaseModel):
    status: Literal["ok", "degraded"]
    environment: str
    market_provider: str
    news_provider: str
    fixture_mode: bool
    database_mode: DatabaseMode
    database_path: str
    database_message: str | None = None
    executor_mode: ExecutorMode
    executor_message: str | None = None
    market_provider_status: SourceStatus
    market_provider_message: str | None = None
    news_provider_status: SourceStatus
    news_provider_message: str | None = None
