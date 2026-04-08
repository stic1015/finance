# Finance Quant Lab Workspace Rules

## Product Mission

Build a single-user quantitative research website for US, Hong Kong, and mainland A-share markets. The site must help the operator inspect market state, connect symbols to relevant news, test systematic strategies, and view 5-trading-day forecast scenarios.

## Non-Negotiable Modeling Rules

1. Forecasts are probabilistic research outputs.
   - Never present a forecast as a guaranteed outcome.
   - Always attach scenario probabilities, expected range, and a non-investment-advice disclaimer.
2. Backtests must be bias-aware.
   - Prevent future leakage in feature generation and signal evaluation.
   - Avoid survivorship bias where feasible and document limits where not yet handled.
   - Keep parameter summaries and benchmark comparisons in every result.
3. Provider truth matters.
   - Real-time or historical market data must flow through provider adapters.
   - Mock or fixture data may be used only for offline development and must be labeled clearly as `fixture`.
   - News must also flow through adapters and keep source attribution.

## Architecture Guardrails

1. Frontend is fixed to `Vue 3 + Vite + TypeScript`, deployed on Vercel.
2. Backend is fixed to local `FastAPI` on Windows with HTTPS exposure through a secure tunnel.
3. Frontend and backend stay separated.
4. Long-running backtests and forecasts must execute asynchronously and expose job status.
5. Storage is split by purpose:
   - SQLite for config, watchlists, job metadata, and lightweight indexes
   - Parquet and DuckDB for historical market data, features, and cached analytics

## UX and Presentation Rules

1. The product style is `AI Quant Lab`.
   - Desktop-first
   - Dark research-terminal feel
   - Blue/cyan accents
   - Dense but well-separated information blocks
2. The key product surfaces are:
   - Market Overview
   - Stock Research
   - Strategy Lab
3. States must be explicit.
   - Show when a provider is live, delayed, unavailable, or fixture-based.
   - Empty news, missing forecasts, and disconnected market feeds must degrade gracefully.

## Engineering Rules

1. Keep provider integrations behind interfaces so Futu, Alpha Vantage, and future sources can swap cleanly.
2. Prefer deterministic, testable pure functions for signal generation, metrics, and feature engineering.
3. Document every public API contract with Pydantic or TypeScript types.
4. When data is unavailable, return explicit structured errors or empty states, never silently invented values.
5. Any future automation, training job, or scheduler must write readable logs and avoid blocking request threads.

## Delivery Expectations

1. Every backtest result must include:
   - date range
   - symbol
   - strategy
   - parameters
   - benchmark comparison
   - return and risk metrics
2. Every forecast result must include:
   - horizon
   - scenario probabilities
   - expected return range
   - model family
   - caveat text
3. Every UI change should preserve the research-first mental model instead of turning the product into a marketing site.
