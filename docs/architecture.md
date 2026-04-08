# Architecture Overview

## Topology

- `frontend/`: Vue 3 SPA deployed to Vercel
- `backend/`: FastAPI application running locally
- `Cloudflare Tunnel`: exposes local backend to Vercel over HTTPS
- `Futu OpenD`: primary market data bridge for US/HK/CN symbols
- `Alpha Vantage`: primary news sentiment source

## Service Domains

### Market Data

- Normalizes symbols across US, HK, SH, and SZ
- Fetches overview cards, snapshots, candles, and live websocket updates
- Labels source status as `live`, `delayed`, `fixture`, or `unavailable`

### News

- Pulls ticker-based sentiment news
- Falls back to keyword expansion using aliases
- Deduplicates by URL and title similarity

### Backtest

- Runs template strategies with explicit parameters
- Caches results and stores run metadata
- Exposes metrics, benchmark comparison, and diagnostics

### Forecast

- Builds technical features from candle history
- Fits classification and regression models for a 5-session horizon
- Returns scenario probabilities and expected range, never certainty

## Storage

- SQLite: config, watchlist, jobs, news index
- Parquet: candles, feature frames, backtest snapshots, forecast artifacts
- DuckDB: analytic reads over cached Parquet files

## Background Jobs

- APScheduler handles refresh windows and nightly model updates
- Process pool handles CPU-bound backtests and forecast jobs
