import { describe, expect, it } from 'vitest'

import type { HealthResponse, NewsFeedResponse } from '../src/types'
import {
  buildProviderBadgeLabel,
  buildRuntimeSummary,
  getHealthHeadline,
  getNewsEmptyMessage,
} from '../src/utils/presentation'

const baseHealth: HealthResponse = {
  status: 'degraded',
  environment: 'development',
  market_provider: 'futu',
  news_provider: 'alpha_vantage',
  fixture_mode: true,
  database_mode: 'memory',
  database_path: 'memory://finance',
  database_message: 'SQLite unavailable; using memory.',
  executor_mode: 'thread_pool',
  executor_message: 'Thread pool fallback active.',
  market_provider_status: 'fixture',
  market_provider_message: 'OpenD is not reachable.',
  news_provider_status: 'unavailable',
  news_provider_message: 'API key missing.',
}

describe('runtime helpers', () => {
  it('builds provider badge labels from provider and status', () => {
    expect(buildProviderBadgeLabel('futu', 'fixture')).toBe('futu 路 fixture')
  })

  it('summarizes local runtime modes', () => {
    expect(buildRuntimeSummary(baseHealth)).toContain('DB memory')
    expect(buildRuntimeSummary(baseHealth)).toContain('fixture fallback enabled')
  })

  it('prefers concrete degraded headlines from health payloads', () => {
    expect(getHealthHeadline(baseHealth)).toContain('OpenD is not reachable')
  })

  it('maps missing news credentials to a user-facing explanation', () => {
    const feed: NewsFeedResponse = {
      symbol: 'US.AAPL',
      provider: 'alpha_vantage',
      source_status: 'unavailable',
      items: [],
      empty_reason: 'missing_api_key',
      message: 'Missing key.',
    }
    expect(getNewsEmptyMessage(feed)).toContain('Alpha Vantage key is missing')
  })
})
