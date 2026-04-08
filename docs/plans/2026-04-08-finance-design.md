# Finance Quant Lab Design Record

## Goal

Create a research-grade quantitative investment website for US, Hong Kong, and A-share markets with live market monitoring, related news, backtesting, and 5-trading-day forecast scenarios.

## Chosen Direction

- Product type: single-user research MVP
- Frontend: Vue 3 on Vercel
- Backend: local FastAPI over secure tunnel
- Design language: AI quant laboratory
- Strategy model: fixed built-in templates with tunable parameters
- Forecast model: probabilistic scenario engine for a 5-session horizon

## Tradeoffs Accepted

- The first version favors a strong architecture and usable demo path over full production data contracts.
- Provider adapters are implemented now, but live credentials remain optional at setup time.
- Fixture mode exists only to keep local development and UI verification moving; it must never masquerade as live data.

## Success Criteria

- A user can inspect overview data for US/HK/CN
- A stock research page shows price, candles, news, backtest, and forecast
- A strategy lab run returns benchmark-aware results with clear caveats
