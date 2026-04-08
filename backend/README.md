# Finance Quant Lab Backend

## Start

```powershell
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
pip install -e .[dev]
uvicorn app.main:app --reload --port 8000
```

## Features

- Market overview, snapshot, candles, and websocket updates
- Related news aggregation with source-aware adapters
- Async backtest jobs with SQLite metadata
- 5-trading-day forecast service with probabilistic scenarios
- Fixture-mode fallback for local UI development

## Optional ML Upgrade

Install the `ml` extra if you want the forecast service to use XGBoost instead of the built-in gradient boosting fallback:

```powershell
. .\.venv\Scripts\Activate.ps1
pip install -e .[ml]
```
