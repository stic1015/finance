<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'

import { apiGet, apiPost } from '@/api/client'
import CandleChart from '@/components/CandleChart.vue'
import MetricTile from '@/components/MetricTile.vue'
import NewsCard from '@/components/NewsCard.vue'
import ProviderBadge from '@/components/ProviderBadge.vue'
import ScenarioCard from '@/components/ScenarioCard.vue'
import SectionPanel from '@/components/SectionPanel.vue'
import { useSystemStore } from '@/stores/system'
import type { BacktestResult, CandleSeries, Forecast5DResult, MarketSnapshot, NewsFeedResponse } from '@/types'
import { compactNumber, formatCurrency, formatMarketPercent, formatPercent } from '@/utils/format'
import { buildProviderBadgeLabel, getNewsEmptyMessage } from '@/utils/runtime'

const route = useRoute()
const symbol = computed(() => String(route.params.symbol ?? 'US.AAPL'))
const systemStore = useSystemStore()

const snapshot = ref<MarketSnapshot | null>(null)
const candles = ref<CandleSeries | null>(null)
const newsFeed = ref<NewsFeedResponse | null>(null)
const forecast = ref<Forecast5DResult | null>(null)
const backtest = ref<BacktestResult | null>(null)
const loading = ref(false)
const error = ref('')

const newsItems = computed(() => newsFeed.value?.items ?? [])
const newsEmptyMessage = computed(() =>
  newsFeed.value ? getNewsEmptyMessage(newsFeed.value) : 'No attributable news yet for this symbol.',
)

async function waitForBacktest(jobId: string) {
  let result = await apiGet<BacktestResult>(`/api/backtests/${jobId}`)
  for (let attempt = 0; attempt < 6 && result.status === 'running'; attempt += 1) {
    await new Promise((resolve) => window.setTimeout(resolve, 1500))
    result = await apiGet<BacktestResult>(`/api/backtests/${jobId}`)
  }
  return result
}

async function loadResearch() {
  loading.value = true
  error.value = ''
  try {
    const [snapshotResponse, candleResponse, newsResponse] = await Promise.all([
      apiGet<MarketSnapshot>(`/api/stocks/${symbol.value}/snapshot`),
      apiGet<CandleSeries>(`/api/stocks/${symbol.value}/candles?interval=1d&limit=200`),
      apiGet<NewsFeedResponse>(`/api/stocks/${symbol.value}/news`),
    ])
    snapshot.value = snapshotResponse
    candles.value = candleResponse
    newsFeed.value = newsResponse
    forecast.value = await apiPost<Forecast5DResult>('/api/forecasts/5d', {
      symbol: symbol.value,
      interval: '1d',
      lookback: 260,
    })
    const job = await apiPost<BacktestResult>('/api/backtests', {
      symbol: symbol.value,
      strategy: 'moving_average_trend',
      start_date: '2024-01-01T00:00:00Z',
      end_date: '2025-01-01T00:00:00Z',
      params: { fast_window: 20, slow_window: 60 },
    })
    backtest.value = await waitForBacktest(job.job_id)
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Failed to load stock research.'
  } finally {
    loading.value = false
  }
}

watch(symbol, () => {
  void loadResearch()
})

onMounted(() => {
  if (!systemStore.health) {
    void systemStore.loadHealth()
  }
  void loadResearch()
})
</script>

<template>
  <div class="research-layout">
    <section class="hero panel" v-if="snapshot">
      <div>
        <div class="eyebrow">{{ snapshot.symbol }}</div>
        <h2>{{ snapshot.display_name }}</h2>
        <div class="hero-price-row">
          <strong>{{ formatCurrency(snapshot.price) }}</strong>
          <span :class="snapshot.change_percent >= 0 ? 'status-positive' : 'status-negative'">
            {{ formatMarketPercent(snapshot.change_percent) }}
          </span>
        </div>
      </div>
      <div class="hero-stats">
        <MetricTile label="Volume" :value="compactNumber(snapshot.volume)" />
        <MetricTile label="Turnover" :value="compactNumber(snapshot.turnover)" />
        <MetricTile label="Session" :value="snapshot.market_state" />
      </div>
    </section>

    <div v-if="loading" class="panel loading-block">Loading research surface...</div>
    <div v-else-if="error" class="panel loading-block error">{{ error }}</div>

    <template v-else>
      <SectionPanel title="Price Structure" subtitle="Candles and volume">
        <div v-if="snapshot || candles" class="section-meta">
          <ProviderBadge
            v-if="snapshot"
            :label="buildProviderBadgeLabel('snapshot', snapshot.source_status)"
            :status="snapshot.source_status"
          />
          <ProviderBadge
            v-if="candles"
            :label="buildProviderBadgeLabel(`candles ${candles.interval}`, candles.source_status)"
            :status="candles.source_status"
          />
        </div>
        <CandleChart :series="candles" />
      </SectionPanel>

      <div class="split-layout">
        <SectionPanel title="Related News" subtitle="Attribution-aware feed">
          <div v-if="newsFeed" class="section-meta">
            <ProviderBadge
              :label="buildProviderBadgeLabel(newsFeed.provider, newsFeed.source_status)"
              :status="newsFeed.source_status"
            />
            <p v-if="newsFeed.message" class="section-note">{{ newsFeed.message }}</p>
          </div>
          <div v-if="newsItems.length" class="news-grid">
            <NewsCard v-for="item in newsItems" :key="item.id" :item="item" />
          </div>
          <div v-else class="empty-state panel">{{ newsEmptyMessage }}</div>
        </SectionPanel>

        <SectionPanel title="5-Day Forecast" subtitle="Scenario distribution">
          <div v-if="forecast" class="section-meta">
            <ProviderBadge
              :label="buildProviderBadgeLabel(`forecast ${forecast.model_family}`, forecast.source_status)"
              :status="forecast.source_status"
            />
            <p class="section-note">Input candles: {{ candles?.source_status ?? 'unknown' }}</p>
          </div>
          <div v-if="forecast" class="scenario-grid">
            <ScenarioCard v-for="scenario in forecast.scenarios" :key="scenario.label" :scenario="scenario" />
            <div class="forecast-summary panel">
              <div class="eyebrow">Expected price band</div>
              <strong>
                {{ formatCurrency(forecast.expected_price_range[0]) }} -
                {{ formatCurrency(forecast.expected_price_range[1]) }}
              </strong>
              <p>{{ forecast.caveat }}</p>
            </div>
          </div>
        </SectionPanel>
      </div>

      <SectionPanel title="Backtest Snapshot" subtitle="Default template run">
        <div v-if="candles || systemStore.health" class="section-meta">
          <ProviderBadge
            v-if="candles"
            :label="buildProviderBadgeLabel('backtest input', candles.source_status)"
            :status="candles.source_status"
          />
          <p v-if="systemStore.health" class="section-note">
            Executor {{ systemStore.health.executor_mode }}
            <span v-if="systemStore.health.executor_message"> · {{ systemStore.health.executor_message }}</span>
          </p>
        </div>
        <div v-if="backtest?.metrics" class="backtest-grid">
          <MetricTile label="Cumulative Return" :value="formatPercent(backtest.metrics.cumulative_return)" />
          <MetricTile label="Annualized" :value="formatPercent(backtest.metrics.annualized_return)" />
          <MetricTile label="Sharpe" :value="backtest.metrics.sharpe_ratio.toFixed(2)" />
          <MetricTile label="Max Drawdown" :value="formatPercent(backtest.metrics.max_drawdown)" />
          <MetricTile label="Win Rate" :value="formatPercent(backtest.metrics.win_rate)" />
          <MetricTile label="Trades" :value="String(backtest.metrics.trade_count)" />
        </div>
        <div v-else class="empty-state panel">Backtest is still initializing.</div>
      </SectionPanel>
    </template>
  </div>
</template>

<style scoped>
.research-layout,
.split-layout,
.news-grid,
.scenario-grid,
.backtest-grid {
  display: grid;
  gap: 20px;
}

.section-meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.hero {
  display: grid;
  grid-template-columns: 1fr 1.2fr;
  gap: 20px;
  padding: 28px;
}

.hero h2 {
  margin: 8px 0;
  font-size: 2.6rem;
  font-family: 'Chakra Petch', sans-serif;
}

.hero-price-row {
  display: flex;
  align-items: baseline;
  gap: 16px;
}

.hero-price-row strong {
  font-size: 3rem;
  font-family: 'Chakra Petch', sans-serif;
}

.hero-stats,
.backtest-grid {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.split-layout {
  grid-template-columns: 1.15fr 0.85fr;
}

.forecast-summary {
  padding: 18px;
}

.forecast-summary strong {
  display: block;
  margin: 12px 0 8px;
  font-size: 1.6rem;
  font-family: 'Chakra Petch', sans-serif;
}

.forecast-summary p,
.section-note {
  margin: 0;
  color: var(--text-secondary);
  line-height: 1.5;
}

.empty-state,
.loading-block {
  padding: 20px;
}

.error {
  color: var(--negative);
}

@media (max-width: 1200px) {
  .hero,
  .split-layout,
  .hero-stats,
  .backtest-grid {
    grid-template-columns: 1fr;
  }
}
</style>
