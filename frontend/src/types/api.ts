export type SourceStatus = 'live' | 'delayed' | 'fixture' | 'unavailable'
export type DatabaseMode = 'sqlite' | 'memory'
export type ExecutorMode = 'process_pool' | 'thread_pool'

export interface NewsItem {
  id: string
  title: string
  summary: string
  url: string
  source: string
  published_at: string
  sentiment: 'positive' | 'neutral' | 'negative'
  score: number
  matched_symbols: string[]
}

export interface NewsFeedResponse {
  symbol: string
  provider: string
  source_status: SourceStatus
  items: NewsItem[]
  empty_reason?: string | null
  message?: string | null
}

export interface MarketMetric {
  label: string
  value: number
  change_percent: number
  symbol: string
}

export interface OverviewSection {
  region: 'US' | 'HK' | 'CN'
  title: string
  source_status: SourceStatus
  metrics: MarketMetric[]
}

export interface MarketSnapshot {
  symbol: string
  display_name: string
  price: number
  change: number
  change_percent: number
  previous_close: number
  open: number
  high: number
  low: number
  volume: number
  turnover: number
  timestamp: string
  market_state: string
  source_status: SourceStatus
}

export interface MarketOverview {
  generated_at: string
  provider: string
  source_status: SourceStatus
  sections: OverviewSection[]
  top_news: NewsItem[]
  watchlist: MarketSnapshot[]
}

export interface StrategyDefinition {
  name: string
  label: string
  description: string
  category: string
  style_tags: string[]
  market_scope: string[]
  logic_summary: string
  default_params: Record<string, number>
}

export interface CandlePoint {
  timestamp: string
  open: number
  high: number
  low: number
  close: number
  volume: number
}

export interface CandleSeries {
  symbol: string
  interval: string
  source_status: SourceStatus
  points: CandlePoint[]
}

export interface ForecastScenario {
  label: 'bullish' | 'neutral' | 'bearish'
  probability: number
  expected_return: number
}

export interface Forecast5DResult {
  symbol: string
  generated_at: string
  horizon_days: number
  model_family: string
  source_status: SourceStatus
  expected_return_range: [number, number]
  expected_price_range: [number, number]
  scenarios: ForecastScenario[]
  rationale: string[]
  caveat: string
}

export interface BacktestMetrics {
  cumulative_return: number
  annualized_return: number
  sharpe_ratio: number
  max_drawdown: number
  win_rate: number
  trade_count: number
  benchmark_return: number
}

export interface EquityPoint {
  timestamp: string
  equity: number
  benchmark_equity: number
}

export interface BacktestResult {
  job_id: string
  symbol: string
  strategy: string
  benchmark_symbol: string
  started_at: string
  completed_at?: string | null
  status: 'queued' | 'running' | 'completed' | 'failed'
  metrics?: BacktestMetrics | null
  equity_curve: EquityPoint[]
  params: Record<string, number | string>
  caveats: string[]
  error?: string | null
}

export interface HealthResponse {
  status: 'ok' | 'degraded'
  environment: string
  market_provider: string
  news_provider: string
  fixture_mode: boolean
  database_mode: DatabaseMode
  database_path: string
  database_message?: string | null
  executor_mode: ExecutorMode
  executor_message?: string | null
  market_provider_status: SourceStatus
  market_provider_message?: string | null
  news_provider_status: SourceStatus
  news_provider_message?: string | null
}
