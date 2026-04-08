import type { HealthResponse, NewsFeedResponse, SourceStatus } from '@/types'

const STATUS_LABELS: Record<SourceStatus, string> = {
  live: 'live',
  delayed: 'delayed',
  fixture: 'fixture',
  unavailable: 'offline',
}

export function buildProviderBadgeLabel(provider: string, status: SourceStatus) {
  return `${provider} · ${STATUS_LABELS[status]}`
}

export function buildRuntimeSummary(health: HealthResponse) {
  const parts = [`DB ${health.database_mode}`, `Jobs ${health.executor_mode}`]
  if (health.fixture_mode) {
    parts.push('fixture fallback enabled')
  }
  return parts.join(' · ')
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
