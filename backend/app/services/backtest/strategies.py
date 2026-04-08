from __future__ import annotations

import pandas as pd

from app.schemas.models import StrategyDefinition


STRATEGIES: dict[str, StrategyDefinition] = {
    "moving_average_trend": StrategyDefinition(
        name="moving_average_trend",
        label="均线趋势跟随",
        description="当短周期均线站上长周期均线时持有，适合作为最基础的趋势模板。",
        category="基础模板",
        style_tags=["趋势", "单资产", "低频"],
        market_scope=["US", "HK", "SH", "SZ"],
        logic_summary="使用快慢均线金叉确认中期趋势，仓位二值化。",
        default_params={"fast_window": 20, "slow_window": 60},
    ),
    "rsi_bollinger_mean_reversion": StrategyDefinition(
        name="rsi_bollinger_mean_reversion",
        label="RSI 布林带均值回归",
        description="当价格跌破布林带下轨且 RSI 超卖时做均值回归，适合震荡区间。",
        category="基础模板",
        style_tags=["均值回归", "震荡", "技术指标"],
        market_scope=["US", "HK", "SH", "SZ"],
        logic_summary="用布林带偏离和 RSI 超卖共振寻找回归窗口。",
        default_params={"window": 20, "std_dev": 2, "rsi_period": 14},
    ),
    "donchian_volume_breakout": StrategyDefinition(
        name="donchian_volume_breakout",
        label="唐奇安通道放量突破",
        description="只在价格创出通道新高且成交量放大时参与突破，过滤假突破。",
        category="基础模板",
        style_tags=["突破", "量价", "趋势"],
        market_scope=["US", "HK", "SH", "SZ"],
        logic_summary="价格突破前高且成交量显著放大时开仓。",
        default_params={"channel_window": 20, "volume_window": 20, "volume_multiplier": 1.2},
    ),
    "macd_trend_confirmation": StrategyDefinition(
        name="macd_trend_confirmation",
        label="MACD 趋势确认",
        description="用 MACD 与 signal 线关系确认趋势是否延续，适合作为中期确认器。",
        category="基础模板",
        style_tags=["趋势", "动量", "技术指标"],
        market_scope=["US", "HK", "SH", "SZ"],
        logic_summary="MACD 上穿并维持在信号线上方时保持多头仓位。",
        default_params={"fast": 12, "slow": 26, "signal": 9},
    ),
    "trend_strength_volatility_filter": StrategyDefinition(
        name="trend_strength_volatility_filter",
        label="趋势强度 + 波动率过滤",
        description="趋势为主、波动率为辅的机构化模板，只在强趋势且波动不过热时提高仓位。",
        category="机构模板",
        style_tags=["趋势", "波动率过滤", "仓位控制"],
        market_scope=["HK", "SH", "SZ", "US"],
        logic_summary="同时要求趋势方向、短期强度和波动率约束成立，仓位在 0 / 0.5 / 1 之间切换。",
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
        label="相对强弱轮动",
        description="用短中期相对强弱切换仓位，偏向持有处于强势状态的单资产。",
        category="机构模板",
        style_tags=["相对强弱", "状态切换", "仓位控制"],
        market_scope=["HK", "SH", "SZ", "US"],
        logic_summary="短周期强弱与中周期趋势同向时满仓，仅中周期趋势成立时半仓。",
        default_params={"short_lookback": 20, "long_lookback": 90, "regime_floor": 0.02},
    ),
    "volume_price_breakout_risk_budget": StrategyDefinition(
        name="volume_price_breakout_risk_budget",
        label="量价突破 + 风险预算",
        description="突破策略加入 ATR 风险预算，波动越大仓位越低，更像真实研究模板。",
        category="机构模板",
        style_tags=["突破", "风险预算", "ATR"],
        market_scope=["HK", "SH", "SZ", "US"],
        logic_summary="价格突破与成交量扩张共振时开仓，再按 ATR 风险预算动态收缩仓位。",
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
        label="多因子评分模板",
        description="用趋势、波动、成交量和相对强弱四类因子打分，生成分层仓位。",
        category="机构模板",
        style_tags=["多因子", "评分", "仓位分层"],
        market_scope=["HK", "SH", "SZ", "US"],
        logic_summary="四个基础因子分别打分，得分越高仓位越高，适合作为研究型模板。",
        default_params={
            "trend_window": 60,
            "momentum_window": 20,
            "volume_window": 20,
            "volatility_window": 20,
            "entry_threshold": 0.5,
        },
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
            <= close.pct_change().rolling(volatility_window * 2).std().fillna(method="bfill")
        ).astype(float)
        score = (trend_factor + momentum_factor + volume_factor + volatility_factor) / 4
        signal = pd.Series(0.0, index=dataframe.index)
        signal[score >= entry_threshold] = score[score >= entry_threshold]
        return signal.fillna(0.0)

    raise ValueError(f"Unsupported strategy: {strategy}")
