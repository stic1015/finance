import type { HealthResponse, NewsFeedResponse, SourceStatus } from '@/types'

const STATUS_LABELS: Record<SourceStatus, string> = {
  live: '实时',
  delayed: '混合',
  fixture: '模拟',
  unavailable: '不可用',
}

const STATUS_LABELS_EN: Record<SourceStatus, string> = {
  live: 'live',
  delayed: 'delayed',
  fixture: 'fixture',
  unavailable: 'offline',
}

const PROVIDER_LABELS: Record<string, string> = {
  futu: '富途',
  fixture: '模拟源',
  alpha_vantage: 'Alpha Vantage',
  keyword: '关键词回补',
  'futu+fixture': '富途/模拟混合',
  'alpha_vantage+keyword': '新闻聚合',
  snapshot: '快照',
  'backtest input': '回测输入',
}

const SCENARIO_LABELS: Record<string, string> = {
  bullish: '看多',
  neutral: '中性',
  bearish: '看空',
}

const SENTIMENT_LABELS: Record<string, string> = {
  positive: '正面',
  neutral: '中性',
  negative: '负面',
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
  return parts.join(' 路 ')
}

export function buildLocalizedRuntimeSummary(health: HealthResponse) {
  const databaseMode = health.database_mode === 'memory' ? '内存仓库' : 'SQLite'
  const executorMode = health.executor_mode === 'thread_pool' ? '线程池' : '进程池'
  const parts = [`存储 ${databaseMode}`, `任务 ${executorMode}`]
  if (health.fixture_mode) {
    parts.push('允许模拟回退')
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
    return '本地研究运行正常。'
  }

  return (
    health.market_provider_message ??
    health.news_provider_message ??
    health.database_message ??
    health.executor_message ??
    '当前运行环境已降级，但主流程仍可继续。'
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
      return '缺少 Alpha Vantage Key，当前无法获取可归因新闻。'
    case 'rate_limited':
      return '新闻源触发频率限制，请稍后重试。'
    case 'provider_unavailable':
      return '新闻源当前不可用，请检查网络或凭据。'
    case 'no_results':
      return '新闻源已响应，但当前标的暂无可归因新闻。'
    case 'keyword_only':
      return '当前仅有关键词回补结果，缺少直接归因新闻。'
    default:
      return '当前标的暂无可归因新闻。'
  }
}
