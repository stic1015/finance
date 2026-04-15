from __future__ import annotations

import pandas as pd

from app.schemas.models import StrategyDefinition


STRATEGIES: dict[str, StrategyDefinition] = {
    "moving_average_trend": StrategyDefinition(
        name="moving_average_trend",
        label="Moving Average Trend",
        description="Hold when the fast moving average stays above the slow moving average.",
        category="Template",
        style_tags=["trend", "single-asset", "low-frequency"],
        market_scope=["US", "HK", "SH", "SZ"],
        logic_summary="Uses fast/slow moving average crossover to follow medium-term trend.",
        default_params={"fast_window": 20, "slow_window": 60},
    ),
    "rsi_bollinger_mean_reversion": StrategyDefinition(
        name="rsi_bollinger_mean_reversion",
        label="RSI Bollinger Mean Reversion",
        description="Looks for oversold mean-reversion when price breaks lower Bollinger band and RSI is weak.",
        category="Template",
        style_tags=["mean-reversion", "range", "indicator"],
        market_scope=["US", "HK", "SH", "SZ"],
        logic_summary="Combines Bollinger deviation and RSI oversold conditions for mean-reversion entries.",
        default_params={"window": 20, "std_dev": 2, "rsi_period": 14},
    ),
    "donchian_volume_breakout": StrategyDefinition(
        name="donchian_volume_breakout",
        label="Donchian Volume Breakout",
        description="Participates in breakouts only when price breaks prior channel high with volume expansion.",
        category="Template",
        style_tags=["breakout", "volume", "trend"],
        market_scope=["US", "HK", "SH", "SZ"],
        logic_summary="Enters on Donchian channel breakout confirmed by above-average volume.",
        default_params={"channel_window": 20, "volume_window": 20, "volume_multiplier": 1.2},
    ),
    "macd_trend_confirmation": StrategyDefinition(
        name="macd_trend_confirmation",
        label="MACD Trend Confirmation",
        description="Confirms trend persistence through MACD and signal-line relationship.",
        category="Template",
        style_tags=["trend", "momentum", "indicator"],
        market_scope=["US", "HK", "SH", "SZ"],
        logic_summary="Stays long while MACD remains above the signal line.",
        default_params={"fast": 12, "slow": 26, "signal": 9},
    ),
    "trend_strength_volatility_filter": StrategyDefinition(
        name="trend_strength_volatility_filter",
        label="Trend Strength + Volatility Filter",
        description="Institutional-style template: trend direction with momentum and volatility constraints.",
        category="Institutional",
        style_tags=["trend", "volatility-filter", "position-sizing"],
        market_scope=["US", "HK", "SH", "SZ"],
        logic_summary="Allocates 0/0.5/1.0 exposure based on trend, strength, and volatility ratio.",
        default_params={
            "trend_window": 80,
            "strength_window": 20,
            "vol_short": 10,
            "vol_long": 30,
            "max_vol_ratio": 1.15,
        },
    ),
    "relative_strength_regime_rotation": StrategyDefinition(
        name="relative_strength_regime_rotation",
        label="Relative Strength Regime Rotation",
        description="Adjusts exposure using short- and long-horizon relative strength regimes.",
        category="Institutional",
        style_tags=["relative-strength", "regime", "position-sizing"],
        market_scope=["US", "HK", "SH", "SZ"],
        logic_summary="Uses long regime floor for half position and short-term strength for full position.",
        default_params={"short_lookback": 20, "long_lookback": 90, "regime_floor": 0.02},
    ),
    "volume_price_breakout_risk_budget": StrategyDefinition(
        name="volume_price_breakout_risk_budget",
        label="Volume Price Breakout + Risk Budget",
        description="Breakout template with ATR-based risk budgeting for dynamic exposure.",
        category="Institutional",
        style_tags=["breakout", "risk-budget", "atr"],
        market_scope=["US", "HK", "SH", "SZ"],
        logic_summary="Combines channel breakout, volume confirmation, and ATR risk budget sizing.",
        default_params={
            "channel_window": 55,
            "volume_window": 20,
            "volume_multiplier": 1.35,
            "atr_window": 14,
            "risk_budget": 0.018,
        },
    ),
    "multi_factor_scoring": StrategyDefinition(
        name="multi_factor_scoring",
        label="Multi-factor Scoring",
        description="Scores trend, momentum, volume, and volatility factors to derive exposure.",
        category="Institutional",
        style_tags=["multi-factor", "scoring", "layered-exposure"],
        market_scope=["US", "HK", "SH", "SZ"],
        logic_summary="Builds a normalized factor score and enters when score exceeds threshold.",
        default_params={
            "trend_window": 60,
            "momentum_window": 20,
            "volume_window": 20,
            "volatility_window": 20,
            "entry_threshold": 0.5,
        },
    ),
    "sar_ema144_breakout": StrategyDefinition(
        name="sar_ema144_breakout",
        label="SAR + EMA144 Breakout",
        description="Tracks breakouts only when close is above EMA144 and above Parabolic SAR.",
        category="Institutional",
        style_tags=["breakout", "psar", "ema"],
        market_scope=["US", "HK", "SH", "SZ"],
        logic_summary="Long-only signal turns on when close exceeds both EMA144 and PSAR trend support.",
        default_params={"ema_window": 144, "sar_step": 0.02, "sar_max": 0.2},
    ),
    "ema_adx_trend_follow": StrategyDefinition(
        name="ema_adx_trend_follow",
        label="EMA + ADX Trend Follow",
        description="Uses EMA trend alignment and ADX strength confirmation for directional entries.",
        category="Institutional",
        style_tags=["trend", "adx", "confirmation"],
        market_scope=["US", "HK", "SH", "SZ"],
        logic_summary="Long signal requires fast EMA above slow EMA with ADX and directional DI confirmation.",
        default_params={"fast_ema": 21, "slow_ema": 55, "adx_window": 14, "adx_threshold": 22},
    ),
    "volatility_contraction_breakout": StrategyDefinition(
        name="volatility_contraction_breakout",
        label="Volatility Contraction Breakout",
        description="Looks for breakouts after volatility contraction and volume expansion.",
        category="Institutional",
        style_tags=["breakout", "volatility", "volume"],
        market_scope=["US", "HK", "SH", "SZ"],
        logic_summary="Enters only when short volatility contracts, then price breaks out with participation.",
        default_params={
            "lookback": 60,
            "contraction_window": 10,
            "breakout_window": 20,
            "volatility_threshold": 0.75,
        },
    ),
    "keltner_atr_breakout": StrategyDefinition(
        name="keltner_atr_breakout",
        label="Keltner ATR Breakout",
        description="Trend breakout using EMA centerline and ATR channel expansion.",
        category="Institutional",
        style_tags=["keltner", "atr", "trend"],
        market_scope=["US", "HK", "SH", "SZ"],
        logic_summary="Activates long exposure when close breaks above upper Keltner band and exits below centerline.",
        default_params={"ema_window": 34, "atr_window": 20, "atr_multiplier": 1.8},
    ),
    "rsi_trend_pullback": StrategyDefinition(
        name="rsi_trend_pullback",
        label="RSI Trend Pullback",
        description="Buys pullbacks in uptrend when RSI cools and then stabilizes.",
        category="Institutional",
        style_tags=["pullback", "rsi", "trend"],
        market_scope=["US", "HK", "SH", "SZ"],
        logic_summary="Requires trend filter and RSI pullback zone before restoring long exposure.",
        default_params={
            "trend_window": 60,
            "rsi_period": 14,
            "pullback_floor": 38,
            "pullback_ceiling": 52,
        },
    ),
}


def _parabolic_sar(high: pd.Series, low: pd.Series, step: float, max_step: float) -> pd.Series:
    if high.empty:
        return pd.Series(dtype=float, index=high.index)

    sar = [float(low.iloc[0])]
    trend_up = True
    extreme_point = float(high.iloc[0])
    acceleration = step

    for index in range(1, len(high)):
        prev_sar = sar[-1]
        current_sar = prev_sar + acceleration * (extreme_point - prev_sar)

        if trend_up:
            if index >= 2:
                current_sar = min(current_sar, float(low.iloc[index - 1]), float(low.iloc[index - 2]))
            else:
                current_sar = min(current_sar, float(low.iloc[index - 1]))

            if float(low.iloc[index]) < current_sar:
                trend_up = False
                current_sar = extreme_point
                extreme_point = float(low.iloc[index])
                acceleration = step
            else:
                if float(high.iloc[index]) > extreme_point:
                    extreme_point = float(high.iloc[index])
                    acceleration = min(acceleration + step, max_step)
        else:
            if index >= 2:
                current_sar = max(current_sar, float(high.iloc[index - 1]), float(high.iloc[index - 2]))
            else:
                current_sar = max(current_sar, float(high.iloc[index - 1]))

            if float(high.iloc[index]) > current_sar:
                trend_up = True
                current_sar = extreme_point
                extreme_point = float(high.iloc[index])
                acceleration = step
            else:
                if float(low.iloc[index]) < extreme_point:
                    extreme_point = float(low.iloc[index])
                    acceleration = min(acceleration + step, max_step)

        sar.append(current_sar)

    return pd.Series(sar, index=high.index, dtype=float)


def _average_true_range(dataframe: pd.DataFrame, window: int) -> pd.Series:
    close = dataframe["close"]
    true_range = pd.concat(
        [
            dataframe["high"] - dataframe["low"],
            (dataframe["high"] - close.shift(1)).abs(),
            (dataframe["low"] - close.shift(1)).abs(),
        ],
        axis=1,
    ).max(axis=1)
    return true_range.rolling(window).mean()


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

    if strategy == "trend_strength_volatility_filter":
        trend_window = int(params.get("trend_window", 80))
        strength_window = int(params.get("strength_window", 20))
        vol_short = int(params.get("vol_short", 10))
        vol_long = int(params.get("vol_long", 30))
        max_vol_ratio = float(params.get("max_vol_ratio", 1.15))
        trend_ma = close.rolling(trend_window).mean()
        momentum = close.pct_change(strength_window)
        short_vol = close.pct_change().rolling(vol_short).std()
        long_vol = close.pct_change().rolling(vol_long).std().replace(0, pd.NA)
        vol_ratio = (short_vol / long_vol).fillna(max_vol_ratio + 1)
        strong = (close > trend_ma) & (momentum > 0.03) & (vol_ratio <= max_vol_ratio)
        weak = (close > trend_ma) & (momentum > 0)
        signal = pd.Series(0.0, index=dataframe.index)
        signal[weak] = 0.5
        signal[strong] = 1.0
        return signal.fillna(0.0)

    if strategy == "relative_strength_regime_rotation":
        short_lookback = int(params.get("short_lookback", 20))
        long_lookback = int(params.get("long_lookback", 90))
        regime_floor = float(params.get("regime_floor", 0.02))
        short_strength = close.pct_change(short_lookback)
        long_strength = close.pct_change(long_lookback)
        signal = pd.Series(0.0, index=dataframe.index)
        signal[(long_strength > regime_floor)] = 0.5
        signal[(short_strength > 0) & (long_strength > regime_floor)] = 1.0
        return signal.fillna(0.0)

    if strategy == "volume_price_breakout_risk_budget":
        channel_window = int(params.get("channel_window", 55))
        volume_window = int(params.get("volume_window", 20))
        volume_multiplier = float(params.get("volume_multiplier", 1.35))
        atr_window = int(params.get("atr_window", 14))
        risk_budget = float(params.get("risk_budget", 0.018))
        upper = close.rolling(channel_window).max().shift(1)
        avg_volume = volume.rolling(volume_window).mean()
        true_range = pd.concat(
            [
                dataframe["high"] - dataframe["low"],
                (dataframe["high"] - close.shift(1)).abs(),
                (dataframe["low"] - close.shift(1)).abs(),
            ],
            axis=1,
        ).max(axis=1)
        atr = true_range.rolling(atr_window).mean().replace(0, pd.NA)
        risk_position = (risk_budget / (atr / close).clip(lower=0.001)).clip(upper=1.0).fillna(0.0)
        breakout = (close > upper) & (volume > avg_volume * volume_multiplier)
        signal = pd.Series(0.0, index=dataframe.index)
        signal[breakout] = risk_position[breakout].clip(lower=0.25)
        return signal.replace(0.0, pd.NA).ffill().fillna(0.0)

    if strategy == "multi_factor_scoring":
        trend_window = int(params.get("trend_window", 60))
        momentum_window = int(params.get("momentum_window", 20))
        volume_window = int(params.get("volume_window", 20))
        volatility_window = int(params.get("volatility_window", 20))
        entry_threshold = float(params.get("entry_threshold", 0.5))
        trend_factor = (close > close.rolling(trend_window).mean()).astype(float)
        momentum_factor = (close.pct_change(momentum_window) > 0).astype(float)
        volume_factor = (volume > volume.rolling(volume_window).mean()).astype(float)
        volatility_factor = (
            close.pct_change().rolling(volatility_window).std()
            <= close.pct_change().rolling(volatility_window * 2).std().bfill()
        ).astype(float)
        score = (trend_factor + momentum_factor + volume_factor + volatility_factor) / 4
        signal = pd.Series(0.0, index=dataframe.index)
        signal[score >= entry_threshold] = score[score >= entry_threshold]
        return signal.fillna(0.0)

    if strategy == "sar_ema144_breakout":
        ema_window = int(params.get("ema_window", 144))
        sar_step = float(params.get("sar_step", 0.02))
        sar_max = float(params.get("sar_max", 0.2))
        ema = close.ewm(span=ema_window, adjust=False).mean()
        psar = _parabolic_sar(dataframe["high"], dataframe["low"], sar_step, sar_max)
        signal = ((close > ema) & (close > psar)).astype(float)
        return signal.replace(0.0, pd.NA).ffill().fillna(0.0)

    if strategy == "ema_adx_trend_follow":
        fast_ema = int(params.get("fast_ema", 21))
        slow_ema = int(params.get("slow_ema", 55))
        adx_window = int(params.get("adx_window", 14))
        adx_threshold = float(params.get("adx_threshold", 22))

        ema_fast = close.ewm(span=fast_ema, adjust=False).mean()
        ema_slow = close.ewm(span=slow_ema, adjust=False).mean()

        up_move = dataframe["high"].diff()
        down_move = -dataframe["low"].diff()
        plus_dm = up_move.where((up_move > down_move) & (up_move > 0), 0.0)
        minus_dm = down_move.where((down_move > up_move) & (down_move > 0), 0.0)
        atr = _average_true_range(dataframe, adx_window).replace(0, pd.NA)
        plus_di = 100 * plus_dm.rolling(adx_window).sum() / atr
        minus_di = 100 * minus_dm.rolling(adx_window).sum() / atr
        dx = (100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, pd.NA)).fillna(0.0)
        adx = dx.rolling(adx_window).mean().fillna(0.0)

        signal = (
            (ema_fast > ema_slow)
            & (adx >= adx_threshold)
            & (plus_di.fillna(0.0) > minus_di.fillna(0.0))
        ).astype(float)
        return signal.replace(0.0, pd.NA).ffill().fillna(0.0)

    if strategy == "volatility_contraction_breakout":
        lookback = int(params.get("lookback", 60))
        contraction_window = int(params.get("contraction_window", 10))
        breakout_window = int(params.get("breakout_window", 20))
        volatility_threshold = float(params.get("volatility_threshold", 0.75))

        returns = close.pct_change()
        short_vol = returns.rolling(contraction_window).std()
        long_vol = returns.rolling(lookback).std().replace(0, pd.NA)
        vol_ratio = (short_vol / long_vol).fillna(volatility_threshold + 1.0)
        contraction = vol_ratio <= volatility_threshold
        breakout = close > close.rolling(breakout_window).max().shift(1)
        volume_confirm = volume > volume.rolling(20).mean()

        signal = (contraction & breakout & volume_confirm).astype(float)
        return signal.replace(0.0, pd.NA).ffill().fillna(0.0)

    if strategy == "keltner_atr_breakout":
        ema_window = int(params.get("ema_window", 34))
        atr_window = int(params.get("atr_window", 20))
        atr_multiplier = float(params.get("atr_multiplier", 1.8))

        ema = close.ewm(span=ema_window, adjust=False).mean()
        atr = _average_true_range(dataframe, atr_window)
        upper = ema + atr_multiplier * atr

        entry = close > upper
        exit_signal = close < ema
        signal = pd.Series(0.0, index=dataframe.index)
        signal[entry] = 1.0
        signal[exit_signal] = 0.0
        return signal.ffill().fillna(0.0)

    if strategy == "rsi_trend_pullback":
        trend_window = int(params.get("trend_window", 60))
        rsi_period = int(params.get("rsi_period", 14))
        pullback_floor = float(params.get("pullback_floor", 38))
        pullback_ceiling = float(params.get("pullback_ceiling", 52))

        trend_filter = close > close.ewm(span=trend_window, adjust=False).mean()
        delta = close.diff()
        gains = delta.clip(lower=0).rolling(rsi_period).mean()
        losses = -delta.clip(upper=0).rolling(rsi_period).mean()
        rs = gains / losses.replace(0, pd.NA)
        rsi = 100 - (100 / (1 + rs.fillna(0)))

        entry = trend_filter & (rsi >= pullback_floor) & (rsi <= pullback_ceiling) & (close > close.shift(1))
        exit_signal = close < close.ewm(span=trend_window, adjust=False).mean()
        signal = pd.Series(0.0, index=dataframe.index)
        signal[entry] = 1.0
        signal[exit_signal] = 0.0
        return signal.ffill().fillna(0.0)

    raise ValueError(f"Unsupported strategy: {strategy}")
