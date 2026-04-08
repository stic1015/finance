# Structured UI Handoff Spec

## Project

- Name: Finance Quant Lab
- Platform: desktop-first responsive web app
- Visual direction: AI quant laboratory
- Figma status: guide mode, brief ready for push

## Viewports

- Primary desktop canvas: 1440 x 1024
- Secondary laptop canvas: 1280 x 900
- Tablet collapse: 1024 x 768
- Mobile reference: 390 x 844

## Design Keywords

- analytical
- futuristic
- signal-driven
- precise
- calm intensity

## Global Tokens

- Accent: cyan / blue
- Density: medium-high
- Radius: 18px panels, 12px controls
- Spacing system: 8 / 12 / 16 / 24 / 32 / 48
- Surfaces: layered dark graphite with thin luminous borders

## Pages

### 1. Market Overview

- Top bar: product title, provider badges, global search, environment status
- Hero strip: US/HK/CN market session cards and key indices
- Main left: market movers table, macro pulse tiles, latest news stream
- Main right: watchlist, top strategy snapshot, forecast monitor

### 2. Stock Research

- Header: symbol, exchange, session state, latest price, percentage move
- Chart zone: candlestick, volume, timeframe switcher, signal overlay chips
- Insight zone: related news cards, forecast scenario cards, backtest summary
- Utility rail: provider status, benchmark, selected strategy, notes

### 3. Strategy Lab

- Control panel: symbol selector, strategy selector, date range, parameter fields
- Results top: CAGR, Sharpe, drawdown, win rate, trades, benchmark
- Results bottom: equity curve, trade distribution, parameter recap, caveats

## Components

- Provider badge
- Market status chip
- Numeric metric tile
- News card with sentiment marker
- Forecast scenario card
- Strategy parameter form
- Equity curve module
- Watchlist table

## States

- Loading: skeleton bars inside cards and chart placeholders
- Empty news: explicit “No attributable news yet”
- Provider down: warning panel with affected features listed
- Fixture mode: visible badge that differentiates development data from live data
