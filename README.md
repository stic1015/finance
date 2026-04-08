# Finance Quant Lab

Finance Quant Lab is a single-user research-oriented quantitative investment website for US stocks, Hong Kong stocks, and mainland A-shares. It combines a Vue 3 frontend with a local FastAPI backend that exposes market data, related news, backtests, and 5-trading-day forecast scenarios. The long-term deployment model is still Vercel for the frontend plus a tunneled local backend, but the current phase is explicitly local-first.

## Workspace Layout

- `frontend/`: Vue 3 + Vite + TypeScript user interface
- `backend/`: FastAPI service, local task execution, provider adapters
- `docs/`: architecture, deployment, UI handoff, and planning notes
- `data/`: local caches, SQLite state, Parquet files, and model artifacts

## Product Boundaries

- Single-user research station, not a brokerage product
- No order routing or trading execution in V1
- Forecasts are probability scenarios, not deterministic predictions
- Real-time data must come from configured providers, never from unlabeled mock responses

## Core Flows

1. Watch global market overview across US/HK/CN.
2. Open a stock research page for snapshot, candles, related news, backtest, and 5-day forecast.
3. Launch strategy experiments from the strategy lab with parameterized templates.

## Local Startup

### Backend

```powershell
cd D:\Codex\Finance\backend
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
pip install -e .[dev]
uvicorn app.main:app --reload --port 8000
```

### Frontend

```powershell
cd D:\Codex\Finance\frontend
npm install
npm run dev
```

The frontend ships with `D:\Codex\Finance\frontend\.env` pointed at `http://localhost:8000` for local integration.

## Deployment Model

- Frontend: local-first now, Vercel later
- Backend: local Windows host
- Public backend access: Cloudflare Tunnel to local FastAPI

See [local-dev.md](D:\Codex\Finance\docs\local-dev.md) for the current integration workflow and [deployment.md](D:\Codex\Finance\docs\deployment.md) for the later tunnel/Vercel setup.
