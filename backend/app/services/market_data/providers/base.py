from __future__ import annotations

from abc import ABC, abstractmethod

from app.schemas.models import CandleSeries, MarketOverview, MarketSnapshot


class ProviderUnavailableError(RuntimeError):
    pass


class MarketDataProvider(ABC):
    source_name: str = "unknown"

    @abstractmethod
    def get_market_overview(self, watchlist: list[str]) -> MarketOverview:
        raise NotImplementedError

    @abstractmethod
    def get_snapshot(self, symbol: str) -> MarketSnapshot:
        raise NotImplementedError

    @abstractmethod
    def get_candles(self, symbol: str, interval: str = "1d", limit: int = 180) -> CandleSeries:
        raise NotImplementedError
