import type { StrategyDefinition } from '@/types'

export type StrategyField = {
  key: string
  label: string
  min?: number
  step?: number
}

export const STRATEGY_FIELDS: Record<string, StrategyField[]> = {
  moving_average_trend: [
    { key: 'fast_window', label: '快线窗口', min: 2, step: 1 },
    { key: 'slow_window', label: '慢线窗口', min: 5, step: 1 },
  ],
  rsi_bollinger_mean_reversion: [
    { key: 'window', label: '布林窗口', min: 5, step: 1 },
    { key: 'std_dev', label: '标准差倍数', min: 1, step: 0.1 },
    { key: 'rsi_period', label: 'RSI 周期', min: 2, step: 1 },
  ],
  donchian_volume_breakout: [
    { key: 'channel_window', label: '通道窗口', min: 5, step: 1 },
    { key: 'volume_window', label: '量能窗口', min: 5, step: 1 },
    { key: 'volume_multiplier', label: '放量倍数', min: 1, step: 0.05 },
  ],
  macd_trend_confirmation: [
    { key: 'fast', label: '快线 EMA', min: 2, step: 1 },
    { key: 'slow', label: '慢线 EMA', min: 5, step: 1 },
    { key: 'signal', label: '信号线周期', min: 2, step: 1 },
  ],
  trend_strength_volatility_filter: [
    { key: 'trend_window', label: '趋势窗口', min: 20, step: 1 },
    { key: 'strength_window', label: '强度窗口', min: 5, step: 1 },
    { key: 'vol_short', label: '短波动窗口', min: 5, step: 1 },
    { key: 'vol_long', label: '长波动窗口', min: 10, step: 1 },
    { key: 'max_vol_ratio', label: '波动率上限', min: 0.5, step: 0.01 },
  ],
  relative_strength_regime_rotation: [
    { key: 'short_lookback', label: '短周期强弱', min: 5, step: 1 },
    { key: 'long_lookback', label: '长周期强弱', min: 20, step: 1 },
    { key: 'regime_floor', label: '趋势门槛', min: 0.001, step: 0.001 },
  ],
  volume_price_breakout_risk_budget: [
    { key: 'channel_window', label: '突破窗口', min: 20, step: 1 },
    { key: 'volume_window', label: '量能窗口', min: 5, step: 1 },
    { key: 'volume_multiplier', label: '放量倍数', min: 1, step: 0.05 },
    { key: 'atr_window', label: 'ATR 窗口', min: 5, step: 1 },
    { key: 'risk_budget', label: '风险预算', min: 0.001, step: 0.001 },
  ],
  multi_factor_scoring: [
    { key: 'trend_window', label: '趋势窗口', min: 20, step: 1 },
    { key: 'momentum_window', label: '动量窗口', min: 5, step: 1 },
    { key: 'volume_window', label: '量能窗口', min: 5, step: 1 },
    { key: 'volatility_window', label: '波动窗口', min: 5, step: 1 },
    { key: 'entry_threshold', label: '入场阈值', min: 0.25, step: 0.05 },
  ],
}

export const FALLBACK_STRATEGIES: StrategyDefinition[] = [
  {
    name: 'moving_average_trend',
    label: '均线趋势跟随',
    description: '当短周期均线站上长周期均线时持有，适合作为最基础的趋势模板。',
    category: '基础模板',
    style_tags: ['趋势', '单资产', '低频'],
    market_scope: ['US', 'HK', 'SH', 'SZ'],
    logic_summary: '使用快慢均线金叉确认中期趋势，仓位二值化。',
    default_params: { fast_window: 20, slow_window: 60 },
  },
  {
    name: 'rsi_bollinger_mean_reversion',
    label: 'RSI 布林带均值回归',
    description: '当价格跌破布林带下轨且 RSI 超卖时做均值回归，适合震荡区间。',
    category: '基础模板',
    style_tags: ['均值回归', '震荡', '技术指标'],
    market_scope: ['US', 'HK', 'SH', 'SZ'],
    logic_summary: '用布林带偏离和 RSI 超卖共振寻找回归窗口。',
    default_params: { window: 20, std_dev: 2, rsi_period: 14 },
  },
  {
    name: 'donchian_volume_breakout',
    label: '唐奇安通道放量突破',
    description: '只在价格创出通道新高且成交量放大时参与突破，过滤假突破。',
    category: '基础模板',
    style_tags: ['突破', '量价', '趋势'],
    market_scope: ['US', 'HK', 'SH', 'SZ'],
    logic_summary: '价格突破前高且成交量显著放大时开仓。',
    default_params: { channel_window: 20, volume_window: 20, volume_multiplier: 1.2 },
  },
  {
    name: 'macd_trend_confirmation',
    label: 'MACD 趋势确认',
    description: '用 MACD 与 signal 线关系确认趋势是否延续，适合作为中期确认器。',
    category: '基础模板',
    style_tags: ['趋势', '动量', '技术指标'],
    market_scope: ['US', 'HK', 'SH', 'SZ'],
    logic_summary: 'MACD 上穿并维持在信号线上方时保持多头仓位。',
    default_params: { fast: 12, slow: 26, signal: 9 },
  },
  {
    name: 'trend_strength_volatility_filter',
    label: '趋势强度 + 波动率过滤',
    description: '趋势为主、波动率为辅的机构化模板，只在强趋势且波动不过热时提高仓位。',
    category: '机构模板',
    style_tags: ['趋势', '波动率过滤', '仓位控制'],
    market_scope: ['HK', 'SH', 'SZ', 'US'],
    logic_summary: '同时要求趋势方向、短期强度和波动率约束成立，仓位在 0 / 0.5 / 1 之间切换。',
    default_params: { trend_window: 80, strength_window: 20, vol_short: 10, vol_long: 30, max_vol_ratio: 1.15 },
  },
  {
    name: 'relative_strength_regime_rotation',
    label: '相对强弱轮动',
    description: '用短中期相对强弱切换仓位，偏向持有处于强势状态的单资产。',
    category: '机构模板',
    style_tags: ['相对强弱', '状态切换', '仓位控制'],
    market_scope: ['HK', 'SH', 'SZ', 'US'],
    logic_summary: '短周期强弱与中周期趋势同向时满仓，仅中周期趋势成立时半仓。',
    default_params: { short_lookback: 20, long_lookback: 90, regime_floor: 0.02 },
  },
  {
    name: 'volume_price_breakout_risk_budget',
    label: '量价突破 + 风险预算',
    description: '突破策略加入 ATR 风险预算，波动越大仓位越低，更像真实研究模板。',
    category: '机构模板',
    style_tags: ['突破', '风险预算', 'ATR'],
    market_scope: ['HK', 'SH', 'SZ', 'US'],
    logic_summary: '价格突破与成交量扩张共振时开仓，再按 ATR 风险预算动态收缩仓位。',
    default_params: { channel_window: 55, volume_window: 20, volume_multiplier: 1.35, atr_window: 14, risk_budget: 0.018 },
  },
  {
    name: 'multi_factor_scoring',
    label: '多因子评分模板',
    description: '用趋势、波动、成交量和相对强弱四类因子打分，生成分层仓位。',
    category: '机构模板',
    style_tags: ['多因子', '评分', '仓位分层'],
    market_scope: ['HK', 'SH', 'SZ', 'US'],
    logic_summary: '四个基础因子分别打分，得分越高仓位越高，适合作为研究型模板。',
    default_params: { trend_window: 60, momentum_window: 20, volume_window: 20, volatility_window: 20, entry_threshold: 0.5 },
  },
]
