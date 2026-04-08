# Finance Quant Lab Design System

## Product Direction

Finance Quant Lab should feel like an advanced AI-assisted research desk rather than a retail brokerage page. The interface must signal rigor, speed, and technical depth while staying readable during long sessions.

## Visual Identity

- Theme: dark, cinematic, instrument-panel inspired
- Mood: precise, futuristic, calm, analytical
- Avoid: purple-heavy gradients, playful illustrations, bright retail trading colors
- Signature memory: cyan signal glow over deep graphite surfaces with subtle grid textures

## Color System

### Core Surfaces

- Page background: `#07111b`
- Elevated surface: `#0c1824`
- Panel surface: `#102131`
- Border: `rgba(140, 196, 230, 0.16)`
- Hairline highlight: `rgba(153, 235, 255, 0.22)`

### Text

- Primary text: `#eff7ff`
- Secondary text: `#98afc5`
- Muted text: `#65819a`

### Brand / Accents

- Accent primary: `#37d6ff`
- Accent secondary: `#18b6d9`
- Accent glow: `rgba(55, 214, 255, 0.28)`

### State Colors

- Bullish / positive: `#2fe08b`
- Bearish / negative: `#ff6b7a`
- Warning: `#ffbf5a`
- Neutral / info: `#5caeff`

## Typography

- Display font: `Chakra Petch`
- UI / body font: `IBM Plex Sans`
- Monospace: `IBM Plex Mono`

### Type Scale

- Hero number: 40px
- Page title: 28px
- Section title: 20px
- Card label: 13px uppercase
- Body: 15px
- Meta / helper: 12px

## Layout Rules

1. Desktop-first with responsive collapse below 1200px and 820px.
2. Use strong panel framing and large spacing between zones.
3. Prioritize left-to-right analytic flow:
   - market state
   - price context
   - explanatory signals
   - actions and scenario outputs
4. Charts must own visual focus and never compete with decorative elements.

## Component Language

### Shell

- Background includes soft radial gradients plus a low-contrast grid
- Sticky top navigation with research-desk look
- Panels use 18-24px radius, thin borders, subtle inner highlights

### Cards

- Use top labels and strong numeric hierarchy
- Avoid heavy shadows; prefer glow rings and border contrast
- Important cards can use gradient edge strips instead of filled backgrounds

### Charts

- Candles on deep background
- Grid lines faint and cool-toned
- Positive candles green, negative candles red
- Forecast band uses cyan to blue transparency

### News

- News cards are compact and scan-friendly
- Always show source, time, sentiment, and matched ticker context
- Empty state must say whether the issue is missing attribution or missing provider data

### Backtest Results

- Show headline metrics first
- Keep risk metrics near return metrics
- Trade logs and benchmark summary go below the fold

## Page Specs

### Market Overview

- Hero row: global status ribbon, search, provider state
- Left main zone: regional market cards, trend boards, latest composite news
- Right utility rail: watchlist, strategy pulse, forecast monitor

### Stock Research

- Header: symbol identity, price, change, market session
- Main: candle chart, volume, signal overlays
- Lower split: related news, backtest summary, 5-day forecast scenarios

### Strategy Lab

- Left: symbol, timeframe, strategy picker, parameter controls
- Right: performance summary, equity curve, benchmark, diagnostics

## Motion

- Use motion sparingly and meaningfully
- Panels can fade and rise on load
- Value updates should pulse softly, not bounce
- Avoid gimmick animation on charts

## Accessibility

- Maintain strong contrast
- Never rely on color alone for bull/bear states
- Keep keyboard focus visible with cyan focus rings
- Dense layouts still need 44px touch-friendly targets on compact breakpoints
