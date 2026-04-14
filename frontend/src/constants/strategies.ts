import type { Locale } from '@/i18n'
import type { StrategyDefinition } from '@/types'

export type StrategyField = {
  key: string
  label: string
  min?: number
  step?: number
}

type LocalizedText = {
  zh: string
  en: string
}

type StrategyMeta = {
  label: LocalizedText
  description: LocalizedText
  category: LocalizedText
  logic_summary: LocalizedText
}

type StrategyFieldMeta = {
  key: string
  min?: number
  step?: number
  label: LocalizedText
}

const META: Record<string, StrategyMeta> = {
  moving_average_trend: {
    label: { zh: '均线趋势跟随', en: 'Moving Average Trend' },
    description: {
      zh: '当快线高于慢线时持有，适合作为最基础的趋势模板。',
      en: 'Hold when the fast moving average is above the slow moving average.',
    },
    category: { zh: '基础模板', en: 'Template' },
    logic_summary: {
      zh: '使用快慢均线关系确认中期趋势。',
      en: 'Uses fast/slow moving average relationship to confirm medium-term trend.',
    },
  },
  rsi_bollinger_mean_reversion: {
    label: { zh: 'RSI 布林带均值回归', en: 'RSI Bollinger Mean Reversion' },
    description: {
      zh: '当价格偏离下轨且 RSI 超卖时寻找回归机会。',
      en: 'Looks for mean reversion when price is below lower band and RSI is oversold.',
    },
    category: { zh: '基础模板', en: 'Template' },
    logic_summary: {
      zh: '结合布林带偏离与 RSI 超卖进行回归入场。',
      en: 'Combines Bollinger deviation and RSI oversold conditions for entry.',
    },
  },
  donchian_volume_breakout: {
    label: { zh: '唐奇安放量突破', en: 'Donchian Volume Breakout' },
    description: {
      zh: '仅在突破前高且成交量放大时参与趋势突破。',
      en: 'Enters breakout only when channel high is broken with volume expansion.',
    },
    category: { zh: '基础模板', en: 'Template' },
    logic_summary: {
      zh: '价格突破 + 成交量确认。',
      en: 'Price breakout plus volume confirmation.',
    },
  },
  macd_trend_confirmation: {
    label: { zh: 'MACD 趋势确认', en: 'MACD Trend Confirmation' },
    description: {
      zh: '通过 MACD 与 signal 线关系确认趋势是否延续。',
      en: 'Uses MACD/signal relationship to confirm trend persistence.',
    },
    category: { zh: '基础模板', en: 'Template' },
    logic_summary: {
      zh: 'MACD 在 signal 上方时维持多头。',
      en: 'Keeps long exposure while MACD is above the signal line.',
    },
  },
  trend_strength_volatility_filter: {
    label: { zh: '趋势强度 + 波动过滤', en: 'Trend Strength + Volatility Filter' },
    description: {
      zh: '趋势、动量、波动三重约束的机构化模板。',
      en: 'Institutional template combining trend, momentum, and volatility constraints.',
    },
    category: { zh: '机构模板', en: 'Institutional' },
    logic_summary: {
      zh: '按趋势强弱与波动状态切换 0/0.5/1 仓位。',
      en: 'Switches 0/0.5/1.0 exposure based on trend and volatility regime.',
    },
  },
  relative_strength_regime_rotation: {
    label: { zh: '相对强弱轮动', en: 'Relative Strength Regime Rotation' },
    description: {
      zh: '利用短中期强弱变化进行仓位轮动。',
      en: 'Rotates exposure using short/long relative strength regimes.',
    },
    category: { zh: '机构模板', en: 'Institutional' },
    logic_summary: {
      zh: '长周期强势给半仓，短周期同向时加满仓。',
      en: 'Half position on long regime strength, full when short strength confirms.',
    },
  },
  volume_price_breakout_risk_budget: {
    label: { zh: '量价突破 + 风险预算', en: 'Volume Breakout + Risk Budget' },
    description: {
      zh: '突破策略叠加 ATR 风险预算，动态控制仓位。',
      en: 'Breakout strategy with ATR-based dynamic risk budgeting.',
    },
    category: { zh: '机构模板', en: 'Institutional' },
    logic_summary: {
      zh: '突破入场后按 ATR 波动率缩放仓位。',
      en: 'Scales exposure by ATR risk budget after breakout confirmation.',
    },
  },
  multi_factor_scoring: {
    label: { zh: '多因子评分', en: 'Multi-factor Scoring' },
    description: {
      zh: '趋势、动量、成交量与波动因子共同评分后决策仓位。',
      en: 'Scores trend, momentum, volume and volatility factors for exposure.',
    },
    category: { zh: '机构模板', en: 'Institutional' },
    logic_summary: {
      zh: '多因子得分超过阈值后入场。',
      en: 'Enters when normalized multi-factor score exceeds threshold.',
    },
  },
  sar_ema144_breakout: {
    label: { zh: 'SAR + EMA144 突破', en: 'SAR + EMA144 Breakout' },
    description: {
      zh: '仅当价格站上 EMA144 且高于抛物线 SAR 时参与。',
      en: 'Enters only when close is above both EMA144 and Parabolic SAR.',
    },
    category: { zh: '机构模板', en: 'Institutional' },
    logic_summary: {
      zh: 'EMA 长趋势过滤 + SAR 趋势支撑双重确认。',
      en: 'Uses EMA trend filter plus PSAR support confirmation.',
    },
  },
}

const FIELD_META: Record<string, StrategyFieldMeta[]> = {
  moving_average_trend: [
    { key: 'fast_window', min: 2, step: 1, label: { zh: '快线窗口', en: 'Fast Window' } },
    { key: 'slow_window', min: 5, step: 1, label: { zh: '慢线窗口', en: 'Slow Window' } },
  ],
  rsi_bollinger_mean_reversion: [
    { key: 'window', min: 5, step: 1, label: { zh: '布林窗口', en: 'Band Window' } },
    { key: 'std_dev', min: 1, step: 0.1, label: { zh: '标准差倍数', en: 'Std Dev Multiplier' } },
    { key: 'rsi_period', min: 2, step: 1, label: { zh: 'RSI 周期', en: 'RSI Period' } },
  ],
  donchian_volume_breakout: [
    { key: 'channel_window', min: 5, step: 1, label: { zh: '通道窗口', en: 'Channel Window' } },
    { key: 'volume_window', min: 5, step: 1, label: { zh: '成交量窗口', en: 'Volume Window' } },
    { key: 'volume_multiplier', min: 1, step: 0.05, label: { zh: '放量倍数', en: 'Volume Multiplier' } },
  ],
  macd_trend_confirmation: [
    { key: 'fast', min: 2, step: 1, label: { zh: '快 EMA', en: 'Fast EMA' } },
    { key: 'slow', min: 5, step: 1, label: { zh: '慢 EMA', en: 'Slow EMA' } },
    { key: 'signal', min: 2, step: 1, label: { zh: '信号周期', en: 'Signal Period' } },
  ],
  trend_strength_volatility_filter: [
    { key: 'trend_window', min: 20, step: 1, label: { zh: '趋势窗口', en: 'Trend Window' } },
    { key: 'strength_window', min: 5, step: 1, label: { zh: '强度窗口', en: 'Strength Window' } },
    { key: 'vol_short', min: 5, step: 1, label: { zh: '短波动窗口', en: 'Short Vol Window' } },
    { key: 'vol_long', min: 10, step: 1, label: { zh: '长波动窗口', en: 'Long Vol Window' } },
    { key: 'max_vol_ratio', min: 0.5, step: 0.01, label: { zh: '波动比上限', en: 'Max Vol Ratio' } },
  ],
  relative_strength_regime_rotation: [
    { key: 'short_lookback', min: 5, step: 1, label: { zh: '短周期回看', en: 'Short Lookback' } },
    { key: 'long_lookback', min: 20, step: 1, label: { zh: '长周期回看', en: 'Long Lookback' } },
    { key: 'regime_floor', min: 0.001, step: 0.001, label: { zh: '趋势门槛', en: 'Regime Floor' } },
  ],
  volume_price_breakout_risk_budget: [
    { key: 'channel_window', min: 20, step: 1, label: { zh: '突破窗口', en: 'Channel Window' } },
    { key: 'volume_window', min: 5, step: 1, label: { zh: '成交量窗口', en: 'Volume Window' } },
    { key: 'volume_multiplier', min: 1, step: 0.05, label: { zh: '放量倍数', en: 'Volume Multiplier' } },
    { key: 'atr_window', min: 5, step: 1, label: { zh: 'ATR 窗口', en: 'ATR Window' } },
    { key: 'risk_budget', min: 0.001, step: 0.001, label: { zh: '风险预算', en: 'Risk Budget' } },
  ],
  multi_factor_scoring: [
    { key: 'trend_window', min: 20, step: 1, label: { zh: '趋势窗口', en: 'Trend Window' } },
    { key: 'momentum_window', min: 5, step: 1, label: { zh: '动量窗口', en: 'Momentum Window' } },
    { key: 'volume_window', min: 5, step: 1, label: { zh: '成交量窗口', en: 'Volume Window' } },
    { key: 'volatility_window', min: 5, step: 1, label: { zh: '波动窗口', en: 'Volatility Window' } },
    { key: 'entry_threshold', min: 0.25, step: 0.05, label: { zh: '入场阈值', en: 'Entry Threshold' } },
  ],
  sar_ema144_breakout: [
    { key: 'ema_window', min: 2, step: 1, label: { zh: 'EMA 窗口', en: 'EMA Window' } },
    { key: 'sar_step', min: 0.001, step: 0.001, label: { zh: 'SAR 步长', en: 'SAR Step' } },
    { key: 'sar_max', min: 0.01, step: 0.01, label: { zh: 'SAR 上限', en: 'SAR Max' } },
  ],
}

function pick(locale: Locale): keyof LocalizedText {
  return locale === 'zh-CN' ? 'zh' : 'en'
}

export function localizeStrategyDefinition(strategy: StrategyDefinition, locale: Locale): StrategyDefinition {
  const localized = META[strategy.name]
  if (!localized) return strategy
  const lang = pick(locale)
  return {
    ...strategy,
    label: localized.label[lang],
    description: localized.description[lang],
    category: localized.category[lang],
    logic_summary: localized.logic_summary[lang],
  }
}

export function localizeStrategies(strategies: StrategyDefinition[], locale: Locale): StrategyDefinition[] {
  return strategies.map((strategy) => localizeStrategyDefinition(strategy, locale))
}

export function getStrategyFields(strategyName: string, locale: Locale): StrategyField[] {
  const lang = pick(locale)
  return (FIELD_META[strategyName] ?? []).map((field) => ({
    key: field.key,
    min: field.min,
    step: field.step,
    label: field.label[lang],
  }))
}

export const FALLBACK_STRATEGIES: StrategyDefinition[] = [
  {
    name: 'moving_average_trend',
    label: 'Moving Average Trend',
    description: 'Hold when the fast moving average is above the slow moving average.',
    category: 'Template',
    style_tags: ['trend', 'single-asset', 'low-frequency'],
    market_scope: ['US', 'HK', 'SH', 'SZ'],
    logic_summary: 'Uses fast/slow moving average relationship to confirm medium-term trend.',
    default_params: { fast_window: 20, slow_window: 60 },
  },
  {
    name: 'rsi_bollinger_mean_reversion',
    label: 'RSI Bollinger Mean Reversion',
    description: 'Looks for mean reversion when price is below lower band and RSI is oversold.',
    category: 'Template',
    style_tags: ['mean-reversion', 'range', 'indicator'],
    market_scope: ['US', 'HK', 'SH', 'SZ'],
    logic_summary: 'Combines Bollinger deviation and RSI oversold conditions for entry.',
    default_params: { window: 20, std_dev: 2, rsi_period: 14 },
  },
  {
    name: 'donchian_volume_breakout',
    label: 'Donchian Volume Breakout',
    description: 'Enters breakout only when channel high is broken with volume expansion.',
    category: 'Template',
    style_tags: ['breakout', 'volume', 'trend'],
    market_scope: ['US', 'HK', 'SH', 'SZ'],
    logic_summary: 'Price breakout plus volume confirmation.',
    default_params: { channel_window: 20, volume_window: 20, volume_multiplier: 1.2 },
  },
  {
    name: 'macd_trend_confirmation',
    label: 'MACD Trend Confirmation',
    description: 'Uses MACD/signal relationship to confirm trend persistence.',
    category: 'Template',
    style_tags: ['trend', 'momentum', 'indicator'],
    market_scope: ['US', 'HK', 'SH', 'SZ'],
    logic_summary: 'Keeps long exposure while MACD is above the signal line.',
    default_params: { fast: 12, slow: 26, signal: 9 },
  },
  {
    name: 'trend_strength_volatility_filter',
    label: 'Trend Strength + Volatility Filter',
    description: 'Institutional template combining trend, momentum, and volatility constraints.',
    category: 'Institutional',
    style_tags: ['trend', 'volatility-filter', 'position-sizing'],
    market_scope: ['US', 'HK', 'SH', 'SZ'],
    logic_summary: 'Switches 0/0.5/1.0 exposure based on trend and volatility regime.',
    default_params: { trend_window: 80, strength_window: 20, vol_short: 10, vol_long: 30, max_vol_ratio: 1.15 },
  },
  {
    name: 'relative_strength_regime_rotation',
    label: 'Relative Strength Regime Rotation',
    description: 'Rotates exposure using short/long relative strength regimes.',
    category: 'Institutional',
    style_tags: ['relative-strength', 'regime', 'position-sizing'],
    market_scope: ['US', 'HK', 'SH', 'SZ'],
    logic_summary: 'Half position on long regime strength, full when short strength confirms.',
    default_params: { short_lookback: 20, long_lookback: 90, regime_floor: 0.02 },
  },
  {
    name: 'volume_price_breakout_risk_budget',
    label: 'Volume Breakout + Risk Budget',
    description: 'Breakout strategy with ATR-based dynamic risk budgeting.',
    category: 'Institutional',
    style_tags: ['breakout', 'risk-budget', 'atr'],
    market_scope: ['US', 'HK', 'SH', 'SZ'],
    logic_summary: 'Scales exposure by ATR risk budget after breakout confirmation.',
    default_params: {
      channel_window: 55,
      volume_window: 20,
      volume_multiplier: 1.35,
      atr_window: 14,
      risk_budget: 0.018,
    },
  },
  {
    name: 'multi_factor_scoring',
    label: 'Multi-factor Scoring',
    description: 'Scores trend, momentum, volume and volatility factors for exposure.',
    category: 'Institutional',
    style_tags: ['multi-factor', 'scoring', 'layered-exposure'],
    market_scope: ['US', 'HK', 'SH', 'SZ'],
    logic_summary: 'Enters when normalized multi-factor score exceeds threshold.',
    default_params: {
      trend_window: 60,
      momentum_window: 20,
      volume_window: 20,
      volatility_window: 20,
      entry_threshold: 0.5,
    },
  },
  {
    name: 'sar_ema144_breakout',
    label: 'SAR + EMA144 Breakout',
    description: 'Enters only when close is above both EMA144 and Parabolic SAR.',
    category: 'Institutional',
    style_tags: ['breakout', 'psar', 'ema'],
    market_scope: ['US', 'HK', 'SH', 'SZ'],
    logic_summary: 'Uses EMA trend filter plus PSAR support confirmation.',
    default_params: { ema_window: 144, sar_step: 0.02, sar_max: 0.2 },
  },
]
