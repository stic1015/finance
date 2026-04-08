# Deployment Guide

This project stays in local-first mode during the current phase. Vercel remains the intended frontend target later, but the immediate goal is to stabilize local real-data research workflows.

## Runtime Model

- Frontend runs on Vercel
- Backend runs locally on Windows
- Cloudflare Tunnel publishes `http://localhost:8000` as an HTTPS origin

## Backend Environment

Create `backend/.env` from `.env.example` and set:

- `APP_ENV`
- `ALLOWED_ORIGINS`
- `SQLITE_PATH`
- `PARQUET_ROOT`
- `MARKET_PROVIDER`
- `FUTU_HOST`
- `FUTU_PORT`
- `ALPHA_VANTAGE_API_KEY`
- `ENABLE_FIXTURE_MODE`

For the local-first workflow, also review [local-dev.md](D:\Codex\Finance\docs\local-dev.md) before opening the frontend.

## Tunnel Setup

1. Install Cloudflare Tunnel (`cloudflared`) on the backend host.
2. Authenticate the machine with your Cloudflare account.
3. Create a tunnel that routes an HTTPS hostname to `http://localhost:8000`.
4. Set the resulting public hostname in the Vercel frontend env var `VITE_API_BASE_URL`.

## Vercel Environment

Set:

- `VITE_API_BASE_URL=https://your-finance-api.example.com`
- `VITE_WS_BASE_URL=wss://your-finance-api.example.com`

## Notes

- CORS must allow only local development origins and the Vercel deployment domain.
- If OpenD or Alpha Vantage keys are missing, the backend remains up but reports degraded source status.
- `/api/system/health` now exposes `database_mode`, `executor_mode`, `market_provider_status`, and `news_provider_status` so the frontend can distinguish live, fixture, and unavailable states.
