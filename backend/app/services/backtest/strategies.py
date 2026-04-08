from __future__ import annotations

import pandas as pd

from app.schemas.models import StrategyDefinition


STRATEGIES: dict[str, StrategyDefinition] = {
    "moving_average_trend": StrategyDefinition(
        name="moving_average_trend",
        label="Moving Average Trend",
        description="Long when the fast moving average is above the slow moving average.",
        default_params={"fast_window": 20, "slow_window": 60},
    ),
    "rsi_bollinger_mean_reversion": StrategyDefinition(
        name="rsi_bollinger_mean_reversion",
        label="RSI + Bollinger Mean Reversion",
        description="Fade oversold Bollinger breakdowns with RSI confirmation.",
        default_params={"window": 20, "std_dev": 2, "rsi_period": 14},
    ),
    "donchian_volume_breakout": StrategyDefinition(
        name="donchian_volume_breakout",
        label="Donchian + Volume Breakout",
        description="Follow breakout moves only when volume confirms the expansion.",
        default_params={"channel_window": 20, "volume_window": 20, "volume_multiplier": 1.2},
    ),
    "macd_trend_confirmation": StrategyDefinition(
        name="macd_trend_confirmation",
        label="MACD Trend Confirmation",
        description="Capture medium-term trends when MACD crosses and stays above signal.",
        default_params={"fast": 12, "slow": 26, "signal": 9},
    ),
}


def build_signal_frame(dataframe: pd.DataFrame, strategy: str, params: dict) -> pd.Series:
    close = dataframe["close"]
    volume = dataframe["volume"]

    if strategy == "moving_average_trend":
        fast = int(params.get("fast_window", 20))
        slow = int(params.get("slow_window", 60))
        fast_ma = close.rolling(fast).mean()
        slow_ma = close.rolling(slow).mean()
        return (fast_ma > slow_ma).astype(float)

    if strategy == "rsi_bollinger_mean_reversion":
        window = int(params.get("window", 20))
        std_dev = float(params.get("std_dev", 2))
        rsi_period = int(params.get("rsi_period", 14))
        delta = close.diff()
        gains = delta.clip(lower=0).rolling(rsi_period).mean()
        losses = -delta.clip(upper=0).rolling(rsi_period).mean()
        rs = gains / losses.replace(0, pd.NA)
        rsi = 100 - (100 / (1 + rs.fillna(0)))
        mid = close.rolling(window).mean()
        band_std = close.rolling(window).std()
        lower = mid - std_dev * band_std
        upper = mid + std_dev * band_std
        entry = (close < lower) & (rsi < 35)
        exit_signal = (close > upper) | (rsi > 60)
        signal = pd.Series(0.0, index=dataframe.index)
        signal[entry] = 1.0
        signal[exit_signal] = 0.0
        return signal.ffill().fillna(0.0)

    if strategy == "donchian_volume_breakout":
        channel_window = int(params.get("channel_window", 20))
        volume_window = int(params.get("volume_window", 20))
        volume_multiplier = float(params.get("volume_multiplier", 1.2))
        upper = close.rolling(channel_window).max().shift(1)
        avg_volume = volume.rolling(volume_window).mean()
        entry = (close > upper) & (volume > avg_volume * volume_multiplier)
        return entry.astype(float).replace(0.0, pd.NA).ffill().fillna(0.0)

    if strategy == "macd_trend_confirmation":
        fast = int(params.get("fast", 12))
        slow = int(params.get("slow", 26))
        signal_period = int(params.get("signal", 9))
        ema_fast = close.ewm(span=fast, adjust=False).mean()
        ema_slow = close.ewm(span=slow, adjust=False).mean()
        macd = ema_fast - ema_slow
        signal_line = macd.ewm(span=signal_period, adjust=False).mean()
        return (macd > signal_line).astype(float)

    raise ValueError(f"Unsupported strategy: {strategy}")
