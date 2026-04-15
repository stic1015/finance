# UI Fallback Spec (Guide Mode)

Date: 2026-04-15
Workspace: D:/Codex/Finance
Reason: Figma plugin is installed globally, but this thread does not expose write tools (`guide_mode`).

## 1. Home / Opportunity Board

Objective:
- Replace multi-column stock fragments with one primary ranked stream.
- Make action intent explicit: `Buy / Watch / Avoid` plus reasons.

Layout:
- Top hero with board title, provider status, update time, refresh cadence.
- Summary tiles: `Universe`, `Scanned`, `Buy`, `Watch`.
- Main board table (single stream):
  - Columns: rank, symbol, display name, action, score, risk score, reasons.
  - Row click-through to `/stocks/:symbol`.
  - Action chips use semantic color mapping:
    - Buy: positive
    - Watch: neutral accent
    - Avoid: negative
- Right rail keeps operational context:
  - Data trust (storage, jobs, HK/CN status)
  - Alert center
  - Watch groups preview
  - Market briefs

Behavior:
- Data source is `/api/markets/opportunities?markets=HK,CN&limit=60`.
- Action filters: `All`, `Buy`, `Watch`, `Avoid`.
- Refresh hint mirrors backend cadence (`refresh_interval_sec=300`).

## 2. Strategy Lab

Objective:
- Keep the clean workbench flow and remove garbled text paths.
- Ensure new institutional strategies are visible and runnable.

Layout:
- Left: strategy controls + strategy summary.
- Right: run status, metrics, trade markers, monthly explainers, trade rows, run comparison.

Strategy metadata source:
- Single source of truth is `frontend/src/constants/strategies-clean.ts`.
- `frontend/src/constants/strategies.ts` re-exports from this file.
- Added strategy set includes:
  - `ema_adx_trend_follow`
  - `volatility_contraction_breakout`
  - `keltner_atr_breakout`
  - `rsi_trend_pullback`

## 3. Stock Research

Objective:
- Keep one coherent research narrative without mojibake text.
- Ensure interval control includes `30m` and drives candles/forecast/backtest requests.

Layout:
- Hero: thesis, summary, price, action buttons, interval selector.
- Main: price structure, drivers/technical/risk pills, attributed news.
- Side: forecast scenarios, backtest snapshot, market context.

Behavior:
- Symbol scope remains HK/CN first.
- If feed is not live, messaging explicitly signals research-only confidence level.

## 4. Visual Direction (for later Figma push)

Tone:
- Dense, terminal-like quant workstation.
- Strong hierarchy with one dominant decision surface per page.

Typography:
- Headline: `Chakra Petch` for tactical identity.
- Body/system status: mono + compact sans for scanning.

Interaction:
- Filter chips for board intent.
- Direct jump from board row to stock research.
- No duplicated “primary” boards on the same page.
