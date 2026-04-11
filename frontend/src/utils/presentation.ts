import type { HealthResponse, NewsFeedResponse, SourceStatus } from '@/types'

const STATUS_LABELS: Record<SourceStatus, string> = {
  live: '\u5b9e\u65f6',
  delayed: '\u6df7\u5408',
  fixture: '\u6a21\u62df',
  unavailable: '\u4e0d\u53ef\u7528',
}

const STATUS_LABELS_EN: Record<SourceStatus, string> = {
  live: 'live',
  delayed: 'delayed',
  fixture: 'fixture',
  unavailable: 'offline',
}

const PROVIDER_LABELS: Record<string, string> = {
  futu: '\u5bcc\u9014',
  fixture: '\u6a21\u62df\u6e90',
  alpha_vantage: 'Alpha Vantage',
  keyword: '\u5173\u952e\u8bcd\u56de\u8865',
  'futu+fixture': '\u5bcc\u9014/\u6a21\u62df\u6df7\u5408',
  'alpha_vantage+keyword': '\u65b0\u95fb\u805a\u5408',
  snapshot: '\u5feb\u7167',
  'backtest input': '\u56de\u6d4b\u8f93\u5165',
}

const SCENARIO_LABELS: Record<string, string> = {
  bullish: '\u770b\u591a',
  neutral: '\u4e2d\u6027',
  bearish: '\u770b\u7a7a',
}

const SENTIMENT_LABELS: Record<string, string> = {
  positive: '\u6b63\u9762',
  neutral: '\u4e2d\u6027',
  negative: '\u8d1f\u9762',
}

const TRADE_ACTION_LABELS: Record<string, string> = {
  buy: '\u4e70\u5165',
  sell: '\u5356\u51fa',
  rebalance: '\u8c03\u4ed3',
}

const TRADE_ACTION_LABELS_EN: Record<string, string> = {
  buy: 'Buy',
  sell: 'Sell',
  rebalance: 'Rebalance',
}

export function translateStatus(status: SourceStatus) {
  return STATUS_LABELS[status]
}

export function translateProvider(provider: string) {
  return PROVIDER_LABELS[provider] ?? provider
}

export function translateScenario(label: string) {
  return SCENARIO_LABELS[label] ?? label
}

export function translateSentiment(label: string) {
  return SENTIMENT_LABELS[label] ?? label
}

export function translateTradeAction(label: string, locale: 'zh-CN' | 'en-US' = 'zh-CN') {
  if (locale === 'en-US') return TRADE_ACTION_LABELS_EN[label] ?? label
  return TRADE_ACTION_LABELS[label] ?? label
}

export function buildProviderBadgeLabel(provider: string, status: SourceStatus) {
  return `${provider} 路 ${STATUS_LABELS_EN[status]}`
}

export function buildLocalizedProviderBadgeLabel(provider: string, status: SourceStatus) {
  return `${translateProvider(provider)} ${translateStatus(status)}`
}

export function buildRuntimeSummary(health: HealthResponse) {
  const parts = [`DB ${health.database_mode}`, `Jobs ${health.executor_mode}`]
  if (health.fixture_mode) {
    parts.push('fixture fallback enabled')
  }
  return parts.join(' / ')
}

export function buildLocalizedRuntimeSummary(health: HealthResponse) {
  const databaseMode = health.database_mode === 'memory' ? '\u5185\u5b58\u4ed3\u5e93' : 'SQLite'
  const executorMode = health.executor_mode === 'thread_pool' ? '\u7ebf\u7a0b\u6c60' : '\u8fdb\u7a0b\u6c60'
  const parts = [`\u5b58\u50a8 ${databaseMode}`, `\u4efb\u52a1 ${executorMode}`]
  if (health.fixture_mode) {
    parts.push('\u5141\u8bb8\u6a21\u62df\u56de\u9000')
  }
  return parts.join(' / ')
}

export function getHealthHeadline(health: HealthResponse) {
  if (health.status === 'ok') {
    return 'Local research runtime is healthy.'
  }

  return (
    health.market_provider_message ??
    health.news_provider_message ??
    health.database_message ??
    health.executor_message ??
    'Local runtime is degraded but still usable.'
  )
}

export function getLocalizedHealthHeadline(health: HealthResponse) {
  if (health.status === 'ok') {
    return '\u672c\u5730\u7814\u7a76\u8fd0\u884c\u6b63\u5e38\u3002'
  }

  return (
    health.market_provider_message ??
    health.news_provider_message ??
    health.database_message ??
    health.executor_message ??
    '\u5f53\u524d\u8fd0\u884c\u73af\u5883\u5df2\u964d\u7ea7\uff0c\u4f46\u4e3b\u6d41\u7a0b\u4ecd\u53ef\u7ee7\u7eed\u3002'
  )
}

export function getNewsEmptyMessage(feed: NewsFeedResponse) {
  switch (feed.empty_reason) {
    case 'missing_api_key':
      return 'Alpha Vantage key is missing, so attributed headlines are unavailable in this environment.'
    case 'rate_limited':
      return 'The news provider is rate-limited right now. Try again after the quota window resets.'
    case 'provider_unavailable':
      return 'The news provider did not respond normally. Check provider status and local network access.'
    case 'no_results':
      return 'The live provider responded, but no attributable headlines matched this symbol.'
    case 'keyword_only':
      return 'Only alias-based fallback coverage is available for this symbol right now.'
    default:
      return 'No attributable news yet for this symbol.'
  }
}

export function getLocalizedNewsEmptyMessage(feed: NewsFeedResponse) {
  switch (feed.empty_reason) {
    case 'missing_api_key':
      return '\u7f3a\u5c11 Alpha Vantage Key\uff0c\u5f53\u524d\u65e0\u6cd5\u83b7\u53d6\u53ef\u5f52\u56e0\u65b0\u95fb\u3002'
    case 'rate_limited':
      return '\u65b0\u95fb\u6e90\u89e6\u53d1\u9891\u7387\u9650\u5236\uff0c\u8bf7\u7a0d\u540e\u91cd\u8bd5\u3002'
    case 'provider_unavailable':
      return '\u65b0\u95fb\u6e90\u5f53\u524d\u4e0d\u53ef\u7528\uff0c\u8bf7\u68c0\u67e5\u7f51\u7edc\u6216\u51ed\u636e\u3002'
    case 'no_results':
      return '\u65b0\u95fb\u6e90\u5df2\u54cd\u5e94\uff0c\u4f46\u5f53\u524d\u6807\u7684\u6682\u65e0\u53ef\u5f52\u56e0\u65b0\u95fb\u3002'
    case 'keyword_only':
      return '\u5f53\u524d\u4ec5\u6709\u5173\u952e\u8bcd\u56de\u8865\u7ed3\u679c\uff0c\u7f3a\u5c11\u76f4\u63a5\u5f52\u56e0\u65b0\u95fb\u3002'
    default:
      return '\u5f53\u524d\u6807\u7684\u6682\u65e0\u53ef\u5f52\u56e0\u65b0\u95fb\u3002'
  }
}
