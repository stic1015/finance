from __future__ import annotations

import math
import os
import socket

from app.core.config import Settings
from app.schemas.models import CandleSeries, MarketOverview, MarketSnapshot, ProviderDiagnostic, SymbolRef
from app.services.market_data.providers.base import ProviderUnavailableError
from app.services.market_data.providers.fixture import FixtureMarketDataProvider
from app.services.market_data.providers.futu import FutuMarketDataProvider
from app.services.market_data.symbol import aliases_for, display_name_for, normalize_symbol, to_futu_code


def _resolve_change_percent(change_percent: float, price: float, previous_close: float) -> float:
    if math.isfinite(change_percent):
        if abs(change_percent) > 1e-9:
            return change_percent
        if previous_close > 0 and abs(price - previous_close) <= 1e-9:
            return 0.0
    if previous_close <= 0:
        return 0.0
    return (price - previous_close) / previous_close * 100


class MarketDataService:
    sample_symbols = ["US.AAPL", "HK.00700", "SH.600519", "SZ.000001"]

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.fixture_provider = FixtureMarketDataProvider()
        self.primary_provider = self._build_primary_provider()

    def _build_primary_provider(self):
        if self.settings.market_provider == "futu":
            return FutuMarketDataProvider(
                self.settings.futu_host,
                self.settings.futu_port,
                self.settings.futu_sdk_appdata_path,
            )
        return self.fixture_provider

    def diagnose(self) -> ProviderDiagnostic:
        if self.settings.market_provider != "futu":
            return ProviderDiagnostic(
                provider=self.fixture_provider.source_name,
                status="fixture",
                detail="Fixture market data is active. Set MARKET_PROVIDER=futu and start OpenD for live quotes.",
                sample_symbols=self.sample_symbols,
            )

        self.settings.futu_sdk_appdata_path.mkdir(parents=True, exist_ok=True)
        os.environ["APPDATA"] = str(self.settings.futu_sdk_appdata_path)
        os.environ["appdata"] = str(self.settings.futu_sdk_appdata_path)

        try:
            import futu  # noqa: F401
        except ImportError:
            fallback_status = "fixture" if self.settings.enable_fixture_mode else "unavailable"
            return ProviderDiagnostic(
                provider="futu",
                status=fallback_status,
                detail=(
                    "The futu Python SDK is not installed. Install futu-api, start OpenD, "
                    "and then restart the backend."
                ),
                sample_symbols=self.sample_symbols,
            )

        try:
            with socket.create_connection((self.settings.futu_host, self.settings.futu_port), timeout=2):
                pass
        except OSError as exc:
            fallback_status = "fixture" if self.settings.enable_fixture_mode else "unavailable"
            return ProviderDiagnostic(
                provider="futu",
                status=fallback_status,
                detail=(
                    f"OpenD is not reachable at {self.settings.futu_host}:{self.settings.futu_port}: {exc}. "
                    "Snapshot and candle requests will fall back to fixture mode when allowed."
                ),
                sample_symbols=self.sample_symbols,
            )

        return ProviderDiagnostic(
            provider="futu",
            status="live",
            detail=(
                f"OpenD is reachable at {self.settings.futu_host}:{self.settings.futu_port}. "
                "Validate entitlements with US.AAPL, HK.00700, SH.600519, and SZ.000001."
            ),
            sample_symbols=self.sample_symbols,
        )

    def describe_symbol(self, raw_symbol: str) -> SymbolRef:
        parts = normalize_symbol(raw_symbol)
        normalized = to_futu_code(raw_symbol)
        return SymbolRef(
            raw=raw_symbol,
            normalized=normalized,
            market=parts.market,
            ticker=parts.ticker,
            display_name=display_name_for(normalized),
            aliases=aliases_for(normalized),
        )

    def get_market_overview(self, watchlist: list[str]) -> MarketOverview:
        if isinstance(self.primary_provider, FutuMarketDataProvider) and self.settings.enable_fixture_mode:
            return self._build_mixed_market_overview(watchlist)
        try:
            overview = self.primary_provider.get_market_overview(watchlist)
        except ProviderUnavailableError:
            if not self.settings.enable_fixture_mode:
                raise
            overview = self.fixture_provider.get_market_overview(watchlist)
        overview.watchlist = [self._normalize_snapshot(snapshot) for snapshot in overview.watchlist]
        return overview

    def get_snapshot(self, symbol: str) -> MarketSnapshot:
        try:
            snapshot = self.primary_provider.get_snapshot(symbol)
        except ProviderUnavailableError:
            if not self.settings.enable_fixture_mode:
                raise
            snapshot = self.fixture_provider.get_snapshot(symbol)
        return self._normalize_snapshot(snapshot)

    def get_candles(self, symbol: str, interval: str = "1d", limit: int = 180) -> CandleSeries:
        try:
            return self.primary_provider.get_candles(symbol, interval=interval, limit=limit)
        except ProviderUnavailableError:
            if not self.settings.enable_fixture_mode:
                raise
            return self.fixture_provider.get_candles(symbol, interval=interval, limit=limit)

    def _build_mixed_market_overview(self, watchlist: list[str]) -> MarketOverview:
        snapshots: list[MarketSnapshot] = []
        sections = []
        used_live = False
        used_fixture = False

        for region in self.primary_provider.region_symbols:
            try:
                section = self.primary_provider.get_overview_section(region)
                used_live = True
            except ProviderUnavailableError:
                section = self.fixture_provider.get_overview_section(region)
                used_fixture = True
            sections.append(section)

        for symbol in watchlist:
            try:
                snapshot = self.primary_provider.get_snapshot(symbol)
                used_live = True
            except ProviderUnavailableError:
                snapshot = self.fixture_provider.get_snapshot(symbol)
                used_fixture = True
            snapshots.append(self._normalize_snapshot(snapshot))

        if used_live and used_fixture:
            provider = f"{self.primary_provider.source_name}+{self.fixture_provider.source_name}"
            source_status = "delayed"
        elif used_live:
            provider = self.primary_provider.source_name
            source_status = "live"
        else:
            provider = self.fixture_provider.source_name
            source_status = "fixture"

        return MarketOverview(
            generated_at=self.fixture_provider.get_market_overview([]).generated_at,
            provider=provider,
            source_status=source_status,
            sections=sections,
            top_news=[],
            watchlist=snapshots,
        )

    def _normalize_snapshot(self, snapshot: MarketSnapshot) -> MarketSnapshot:
        resolved = _resolve_change_percent(
            snapshot.change_percent,
            snapshot.price,
            snapshot.previous_close,
        )
        if abs(resolved - snapshot.change_percent) <= 1e-9:
            return snapshot
        return snapshot.model_copy(update={"change_percent": resolved})
