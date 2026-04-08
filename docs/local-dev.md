# Local Development Guide

## Goal

Use the project as a local research station first, with real providers when available and explicit fixture fallback when they are not.

## Frontend

`D:\Codex\Finance\frontend\.env` points to the local FastAPI server:

```dotenv
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_BASE_URL=ws://localhost:8000
```

Start the frontend:

```powershell
cd D:\Codex\Finance\frontend
npm install
npm run dev
```

## Backend

Create `D:\Codex\Finance\backend\.env` from `.env.example`, then set:

- `MARKET_PROVIDER=futu`
- `FUTU_HOST=127.0.0.1`
- `FUTU_PORT=11111`
- `ALPHA_VANTAGE_API_KEY=...`
- `ENABLE_FIXTURE_MODE=true`

Start the backend:

```powershell
cd D:\Codex\Finance\backend
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
pip install -e .[dev]
pip install futu-api
uvicorn app.main:app --reload --port 8000
```

## OpenD Order

1. Install and start OpenD on the local machine.
2. Confirm the OpenD host and port match `FUTU_HOST` and `FUTU_PORT`.
3. Start the FastAPI backend.
4. Open `/api/system/health` and confirm `market_provider_status` is `live`.
5. Start the frontend and verify the topbar badges no longer show fixture mode.

## Sample Symbols

Use these symbols for minimum cross-market verification:

- `US.AAPL`
- `HK.00700`
- `SH.600519`
- `SZ.000001`

## What Degraded Means

- `database_mode=memory`: SQLite was not writable, so metadata is not persisted across restarts.
- `executor_mode=thread_pool`: process workers were unavailable, so backtests run in the thread fallback.
- `market_provider_status=fixture`: OpenD or the Python SDK is unavailable and candles/snapshots are using fixtures.
- `news_provider_status=unavailable`: Alpha Vantage credentials are missing or the provider request failed.
