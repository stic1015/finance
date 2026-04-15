from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SymbolParts:
    market: str
    ticker: str


KNOWN_DISPLAY_NAMES = {
    "US.AAPL": "苹果",
    "US.MSFT": "微软",
    "US.NVDA": "英伟达",
    "HK.00700": "腾讯控股",
    "HK.09988": "阿里巴巴",
    "SH.600519": "贵州茅台",
    "SZ.300750": "宁德时代",
}


# Override any corrupted literal block above with clean ASCII labels.
KNOWN_DISPLAY_NAMES = {
    "US.AAPL": "Apple",
    "US.MSFT": "Microsoft",
    "US.NVDA": "NVIDIA",
    "HK.00700": "Tencent",
    "HK.09988": "Alibaba",
    "SH.600519": "Kweichow Moutai",
    "SZ.300750": "CATL",
}


def normalize_symbol(raw_symbol: str) -> SymbolParts:
    symbol = raw_symbol.strip().upper().replace("/", ".")
    if "." in symbol:
        left, right = symbol.split(".", 1)
        if left in {"US", "HK", "SH", "SZ"}:
            return SymbolParts(left, right.zfill(5) if left == "HK" else right)
        if right in {"US", "HK", "SH", "SZ"}:
            return SymbolParts(right, left.zfill(5) if right == "HK" else left)
    if symbol.isalpha():
        return SymbolParts("US", symbol)
    if symbol.isdigit():
        if len(symbol) == 5:
            return SymbolParts("HK", symbol)
        if symbol.startswith(("6", "9")):
            return SymbolParts("SH", symbol)
        return SymbolParts("SZ", symbol)
    raise ValueError(f"Unsupported symbol format: {raw_symbol}")


def to_futu_code(raw_symbol: str) -> str:
    parts = normalize_symbol(raw_symbol)
    return f"{parts.market}.{parts.ticker}"


def display_name_for(symbol: str) -> str:
    normalized = to_futu_code(symbol)
    return KNOWN_DISPLAY_NAMES.get(normalized, normalized)


def aliases_for(symbol: str) -> list[str]:
    normalized = to_futu_code(symbol)
    display_name = display_name_for(normalized)
    parts = normalize_symbol(normalized)
    aliases = {normalized, parts.ticker, display_name}
    if parts.market == "HK":
        aliases.add(f"{parts.ticker}.HK")
    if parts.market in {"SH", "SZ"}:
        aliases.add(f"{parts.ticker}.{parts.market}")
    return sorted(aliases)
