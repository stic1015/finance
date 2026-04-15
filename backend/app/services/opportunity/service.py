from __future__ import annotations

import asyncio
import math
import os
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

import pandas as pd

from app.core.config import Settings
from app.schemas.models import (
    CandleSeries,
    MarketOpportunityResponse,
    MarketSnapshot,
    OpportunityAction,
    OpportunityItem,
    SourceStatus,
)
from app.services.market_data.service import MarketDataService
from app.services.market_data.symbol import to_futu_code
from app.services.news.service import NewsService
from app.storage.repositories import MemoryRepository, SQLiteRepository


@dataclass
class _UniverseCache:
    expires_at: datetime
    symbols: list[str]
    provider: str


@dataclass
class _OpportunityCandidate:
    snapshot: MarketSnapshot
    score: float
    risk_score: float
    reasons: list[str]


def _clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


class OpportunityService:
    refresh_interval_sec = 300
    universe_ttl_sec = 24 * 3600
    prefilter_sample_size = 400
    max_scanned_symbols = 180
    news_enrichment_symbols = 100

    fallback_hk_universe = [
        "HK.00700",
        "HK.09988",
        "HK.03690",
        "HK.01810",
        "HK.00981",
        "HK.01211",
        "HK.02318",
        "HK.01398",
        "HK.03988",
        "HK.00939",
        "HK.00005",
        "HK.01024",
        "HK.00941",
        "HK.03888",
        "HK.06618",
    ]
    fallback_cn_universe = [
        "SH.600519",
        "SH.601318",
        "SH.600036",
        "SH.600276",
        "SH.601398",
        "SH.600900",
        "SH.600309",
        "SH.601899",
        "SH.601288",
        "SH.600030",
        "SZ.000001",
        "SZ.000333",
        "SZ.000651",
        "SZ.002594",
        "SZ.300750",
    ]

    def __init__(
        self,
        settings: Settings,
        market_service: MarketDataService,
        news_service: NewsService,
        repository: SQLiteRepository | MemoryRepository,
    ) -> None:
        self.settings = settings
        self.market_service = market_service
        self.news_service = news_service
        self.repository = repository
        self._universe_cache: dict[str, _UniverseCache] = {}
        self._opportunity_cache: dict[str, MarketOpportunityResponse] = {}
        self._lock = asyncio.Lock()

    async def get_opportunities(
        self,
        markets: list[str],
        limit: int = 50,
    ) -> MarketOpportunityResponse:
        normalized_markets = self._normalize_markets(markets)
        cache_key = ",".join(normalized_markets)
        now = datetime.now(tz=UTC)

        cached = self._opportunity_cache.get(cache_key)
        if cached and (now - cached.generated_at).total_seconds() <= self.refresh_interval_sec:
            return cached.model_copy(update={"items": cached.items[:limit]})

        async with self._lock:
            cached = self._opportunity_cache.get(cache_key)
            if cached and (now - cached.generated_at).total_seconds() <= self.refresh_interval_sec:
                return cached.model_copy(update={"items": cached.items[:limit]})

            symbols, universe_provider = self._load_universe(normalized_markets)
            candidates, source_status = await self._scan_and_score(symbols, limit)
            items = self._classify_candidates(candidates)
            provider = f"{universe_provider}+signals"

            response = MarketOpportunityResponse(
                generated_at=datetime.now(tz=UTC),
                refresh_interval_sec=self.refresh_interval_sec,
                provider=provider,
                source_status=source_status,
                universe_size=len(symbols),
                scanned_size=len(candidates),
                items=items[:max(limit, 1)],
            )
            self._opportunity_cache[cache_key] = response
            return response

    def _normalize_markets(self, markets: list[str]) -> list[str]:
        normalized: list[str] = []
        for market in markets:
            token = market.strip().upper()
            if token in {"HK", "CN"} and token not in normalized:
                normalized.append(token)
        return normalized or ["HK", "CN"]

    def _load_universe(self, markets: list[str]) -> tuple[list[str], str]:
        key = ",".join(markets)
        now = datetime.now(tz=UTC)
        cached = self._universe_cache.get(key)
        if cached and cached.expires_at > now:
            return cached.symbols, cached.provider

        symbols: list[str] = []
        provider = "fallback"

        if self.settings.market_provider == "futu":
            futu_symbols = self._load_universe_from_futu(markets)
            if futu_symbols:
                symbols = futu_symbols
                provider = "futu"

        if not symbols:
            symbols = self._fallback_universe(markets)
            provider = "watchlist_fallback"

        deduped = sorted({to_futu_code(symbol) for symbol in symbols})
        self._universe_cache[key] = _UniverseCache(
            expires_at=now + timedelta(seconds=self.universe_ttl_sec),
            symbols=deduped,
            provider=provider,
        )
        return deduped, provider

    def _load_universe_from_futu(self, markets: list[str]) -> list[str]:
        self.settings.futu_sdk_appdata_path.mkdir(parents=True, exist_ok=True)
        os.environ["APPDATA"] = str(self.settings.futu_sdk_appdata_path)
        os.environ["appdata"] = str(self.settings.futu_sdk_appdata_path)

        try:
            import futu as ft
        except Exception:
            return []

        market_values: list[Any] = []
        if "HK" in markets:
            market_values.append(ft.Market.HK)
        if "CN" in markets:
            market_values.extend([ft.Market.SH, ft.Market.SZ])

        symbols: list[str] = []
        try:
            with ft.OpenQuoteContext(host=self.settings.futu_host, port=self.settings.futu_port) as quote_ctx:
                for market in market_values:
                    ret, frame = quote_ctx.get_stock_basicinfo(market=market, stock_type="STOCK")
                    if ret != 0 or frame is None or frame.empty:
                        continue
                    codes = [
                        str(code)
                        for code in frame["code"].tolist()
                        if isinstance(code, str) and code.startswith(("HK.", "SH.", "SZ."))
                    ]
                    symbols.extend(codes)
        except Exception:
            return []
        return symbols

    def _fallback_universe(self, markets: list[str]) -> list[str]:
        symbols: list[str] = []
        if "HK" in markets:
            symbols.extend(self.fallback_hk_universe)
        if "CN" in markets:
            symbols.extend(self.fallback_cn_universe)
        symbols.extend(
            symbol
            for symbol in self.repository.list_watchlist()
            if symbol.startswith("HK.") or symbol.startswith(("SH.", "SZ."))
        )
        return symbols

    async def _scan_and_score(
        self,
        universe: list[str],
        limit: int,
    ) -> tuple[list[_OpportunityCandidate], SourceStatus]:
        sample = universe[: self.prefilter_sample_size]
        snapshots: list[MarketSnapshot] = []
        for symbol in sample:
            try:
                snapshots.append(self.market_service.get_snapshot(symbol))
            except Exception:
                continue

        if not snapshots:
            return [], "unavailable"

        liquid = [
            snapshot
            for snapshot in snapshots
            if snapshot.price > 0
            and snapshot.turnover > 0
            and snapshot.volume > 0
            and snapshot.source_status != "unavailable"
        ]
        liquid.sort(key=lambda item: item.turnover, reverse=True)

        scan_target = min(
            self.max_scanned_symbols,
            max(limit * 6, 120),
            len(liquid),
        )
        selected = liquid[:scan_target]

        candidates: list[_OpportunityCandidate] = []
        for snapshot in selected:
            try:
                candles = self.market_service.get_candles(snapshot.symbol, interval="1d", limit=180)
            except Exception:
                continue
            candidate = self._score_candidate(snapshot, candles)
            candidates.append(candidate)

        candidates.sort(key=lambda item: item.score, reverse=True)
        await self._enrich_news_signal(candidates[: min(len(candidates), self.news_enrichment_symbols)])

        if not candidates:
            return [], "unavailable"

        has_live = any(item.snapshot.source_status == "live" for item in candidates)
        has_delayed = any(item.snapshot.source_status in {"delayed", "fixture"} for item in candidates)
        source_status: SourceStatus
        if has_live:
            source_status = "live"
        elif has_delayed:
            source_status = "delayed"
        else:
            source_status = "unavailable"
        return candidates, source_status

    def _score_candidate(self, snapshot: MarketSnapshot, candles: CandleSeries) -> _OpportunityCandidate:
        closes = pd.Series([point.close for point in candles.points], dtype=float)
        volumes = pd.Series([point.volume for point in candles.points], dtype=float)
        if len(closes) < 80:
            return _OpportunityCandidate(
                snapshot=snapshot,
                score=35.0,
                risk_score=55.0,
                reasons=["Not enough candle history yet. Observe for more data stability first."],
            )

        ema20 = float(closes.ewm(span=20, adjust=False).mean().iloc[-1])
        ema60 = float(closes.ewm(span=60, adjust=False).mean().iloc[-1])
        last_close = float(closes.iloc[-1])
        ret20 = float(last_close / closes.iloc[-21] - 1) if len(closes) > 21 else 0.0
        vol_ratio = float(volumes.iloc[-1] / max(float(volumes.tail(20).mean()), 1.0))
        returns = closes.pct_change().dropna()
        vol_20 = float(returns.tail(20).std()) if not returns.empty else 0.03

        trend_score = 30.0 if (last_close > ema20 > ema60) else (18.0 if last_close > ema20 else 6.0)
        momentum_score = _clamp((ret20 + 0.08) / 0.16 * 20.0, 0.0, 20.0)
        volume_score = _clamp((vol_ratio - 0.8) / 0.9 * 20.0, 0.0, 20.0)
        volatility_quality = _clamp((0.06 - vol_20) / 0.06 * 15.0, 0.0, 15.0)

        score = _clamp(trend_score + momentum_score + volume_score + volatility_quality, 0.0, 100.0)

        risk_score = 0.0
        risk_score += _clamp(vol_20 / 0.06 * 50.0, 0.0, 50.0)
        if ret20 < 0:
            risk_score += 15.0
        if last_close < ema60:
            risk_score += 20.0
        if snapshot.source_status != "live":
            risk_score += 20.0
        risk_score = _clamp(risk_score, 0.0, 100.0)

        reasons: list[str] = []
        if last_close > ema20 > ema60:
            reasons.append("Price is above short and medium EMAs, trend remains aligned.")
        elif last_close > ema20:
            reasons.append("Price is above short EMA but has not fully confirmed medium trend.")
        else:
            reasons.append("Price is below EMA structure, trend quality is weak.")

        if ret20 >= 0.06:
            reasons.append("20-day momentum is above the strength threshold.")
        elif ret20 >= 0:
            reasons.append("20-day momentum remains positive.")
        else:
            reasons.append("20-day momentum has turned weak.")

        if vol_ratio >= 1.3:
            reasons.append("Volume expansion is strong and confirms participation.")
        elif vol_ratio >= 1.0:
            reasons.append("Volume is above average and gives moderate confirmation.")
        else:
            reasons.append("Volume is below average and breakout confirmation is weak.")

        if vol_20 > 0.05:
            reasons.append("Recent volatility is elevated and adds risk.")
        else:
            reasons.append("Recent volatility is within a controlled range.")

        return _OpportunityCandidate(
            snapshot=snapshot,
            score=round(score, 2),
            risk_score=round(risk_score, 2),
            reasons=reasons[:5],
        )

    async def _enrich_news_signal(self, candidates: list[_OpportunityCandidate]) -> None:
        semaphore = asyncio.Semaphore(8)

        async def enrich(candidate: _OpportunityCandidate) -> None:
            async with semaphore:
                try:
                    feed = await self.news_service.get_news_for_symbol(candidate.snapshot.symbol)
                except Exception:
                    return
                if not feed.items:
                    return

                positive_count = sum(1 for item in feed.items[:8] if item.sentiment == "positive")
                negative_count = sum(1 for item in feed.items[:8] if item.sentiment == "negative")
                bonus = positive_count * 2.0 - negative_count * 2.5
                bonus = _clamp(bonus, -10.0, 15.0)
                candidate.score = round(_clamp(candidate.score + bonus, 0.0, 100.0), 2)
                if bonus > 1:
                    candidate.reasons.append("Recent news tone is supportive and strengthens the setup.")
                elif bonus < -1:
                    candidate.risk_score = round(_clamp(candidate.risk_score + 8.0, 0.0, 100.0), 2)
                    candidate.reasons.append("Recent news tone is negative and increases risk.")

        await asyncio.gather(*(enrich(candidate) for candidate in candidates))

    def _classify_candidates(self, candidates: list[_OpportunityCandidate]) -> list[OpportunityItem]:
        def to_action(candidate: _OpportunityCandidate) -> OpportunityAction:
            if candidate.snapshot.source_status == "unavailable":
                return "avoid"
            if candidate.score >= 72 and candidate.risk_score <= 25:
                return "buy"
            if candidate.score < 50:
                return "avoid"
            return "watch"

        action_rank = {"buy": 0, "watch": 1, "avoid": 2}
        items: list[OpportunityItem] = []
        for candidate in candidates:
            action = to_action(candidate)
            reasons = list(dict.fromkeys(candidate.reasons))
            if action == "watch" and candidate.score >= 72 and candidate.risk_score > 25:
                reasons.append("High score but risk is still elevated. Keep it on watch.")
            if action == "avoid" and candidate.score < 50:
                reasons.append("Composite score is below execution threshold.")

            items.append(
                OpportunityItem(
                    symbol=candidate.snapshot.symbol,
                    display_name=candidate.snapshot.display_name,
                    price=candidate.snapshot.price,
                    change_percent=candidate.snapshot.change_percent,
                    action=action,
                    score=round(_clamp(candidate.score, 0.0, 100.0), 2),
                    risk_score=round(_clamp(candidate.risk_score, 0.0, 100.0), 2),
                    reasons=reasons[:5],
                )
            )

        items.sort(key=lambda item: (action_rank[item.action], -item.score, item.risk_score))
        return items
