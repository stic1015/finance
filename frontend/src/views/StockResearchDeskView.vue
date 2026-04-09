<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'

import { apiGet, apiPost } from '@/api/client'
import CandleChart from '@/components/CandleChart.vue'
import InsightPill from '@/components/InsightPill.vue'
import MetricTile from '@/components/MetricTile.vue'
import NewsCard from '@/components/NewsCard.vue'
import ProviderBadge from '@/components/ProviderBadge.vue'
import ScenarioCard from '@/components/ScenarioCard.vue'
import SectionPanel from '@/components/SectionPanel.vue'
import { useLocaleStore } from '@/stores/locale'
import { type AlertEvent, type AlertRule, useWatchStore } from '@/stores/watch'
import { useSystemStore } from '@/stores/system'
import type { BacktestResult, CandleSeries, Forecast5DResult, MarketOverview, MarketSnapshot, NewsFeedResponse } from '@/types'
import { compactNumber, formatCurrency, formatMarketPercent, formatPercent } from '@/utils/format'
import { buildLocalizedProviderBadgeLabel, getLocalizedNewsEmptyMessage } from '@/utils/presentation'

const route = useRoute()
const localeStore = useLocaleStore()
const systemStore = useSystemStore()
const watchStore = useWatchStore()
const symbol = computed(() => String(route.params.symbol ?? 'HK.00700'))
type PillTone = 'neutral' | 'positive' | 'negative'

const snapshot = ref<MarketSnapshot | null>(null)
const candles = ref<CandleSeries | null>(null)
const newsFeed = ref<NewsFeedResponse | null>(null)
const forecast = ref<Forecast5DResult | null>(null)
const backtest = ref<BacktestResult | null>(null)
const overview = ref<MarketOverview | null>(null)
const loading = ref(false)
const error = ref('')

const newsItems = computed(() => newsFeed.value?.items ?? [])
const newsEmptyMessage = computed(() =>
  newsFeed.value ? getLocalizedNewsEmptyMessage(newsFeed.value) : localeStore.t('common.noAttributedNews'),
)

const summaryBullets = computed(() => {
  if (!snapshot.value || !forecast.value) return []
  const items = []
  if (snapshot.value.change_percent > 2) items.push(`日内涨幅 ${formatMarketPercent(snapshot.value.change_percent)}`)
  if (forecast.value.scenarios[0]) {
    const leader = [...forecast.value.scenarios].sort((a, b) => b.probability - a.probability)[0]
    items.push(`主导场景 ${leader.label}`)
  }
  if (newsItems.value.length) items.push(`新闻线索 ${newsItems.value.length} 条`)
  if (snapshot.value.source_status !== 'live') items.push('当前并非完整实时权限')
  return items
})

const driverTags = computed<{ label: string; tone: PillTone }[]>(() => {
  if (!snapshot.value || !forecast.value) return []
  const leader = [...forecast.value.scenarios].sort((a, b) => b.probability - a.probability)[0]
  return [
    { label: snapshot.value.change_percent >= 0 ? '价格强于昨日' : '价格弱于昨日', tone: snapshot.value.change_percent >= 0 ? 'positive' : 'negative' as const },
    { label: `成交量 ${compactNumber(snapshot.value.volume)}`, tone: 'neutral' as const },
    { label: `主导场景 ${leader.label}`, tone: 'neutral' as const },
  ]
})

const technicalTags = computed<{ label: string; tone: PillTone }[]>(() => {
  if (!candles.value?.points.length) return []
  const latest = candles.value.points.at(-1)!
  const shortAverage = candles.value.points.slice(-20).reduce((sum, point) => sum + point.close, 0) / Math.min(candles.value.points.length, 20)
  return [
    { label: latest.close >= shortAverage ? '价格站上 20 日均值' : '价格低于 20 日均值', tone: latest.close >= shortAverage ? 'positive' : 'negative' as const },
    { label: latest.close >= latest.open ? '日线结构偏强' : '日线结构偏弱', tone: latest.close >= latest.open ? 'positive' : 'negative' as const },
  ]
})

const riskTags = computed<{ label: string; tone: PillTone }[]>(() => {
  const tags: { label: string; tone: PillTone }[] = []
  if (snapshot.value?.source_status !== 'live') tags.push({ label: localeStore.t('common.restricted'), tone: 'negative' as const })
  if (newsFeed.value?.source_status === 'unavailable') tags.push({ label: '新闻源不可用', tone: 'negative' as const })
  if (forecast.value && forecast.value.scenarios.some((item) => item.label === 'bearish' && item.probability > 0.4)) {
    tags.push({ label: '下行情景概率偏高', tone: 'negative' as const })
  }
  return tags
})

const relativeStrength = computed(() => {
  if (!overview.value || !snapshot.value) return null
  const region = symbol.value.startsWith('HK') ? 'HK' : 'CN'
  const section = overview.value.sections.find((item) => item.region === region)
  if (!section?.metrics.length) return null
  const average = section.metrics.reduce((sum, metric) => sum + metric.change_percent, 0) / section.metrics.length
  return snapshot.value.change_percent - average
})

async function waitForBacktest(jobId: string) {
  let result = await apiGet<BacktestResult>(`/api/backtests/${jobId}`)
  for (let attempt = 0; attempt < 6 && result.status === 'running'; attempt += 1) {
    await new Promise((resolve) => window.setTimeout(resolve, 1500))
    result = await apiGet<BacktestResult>(`/api/backtests/${jobId}`)
  }
  return result
}

function emitLocalAlerts() {
  if (!snapshot.value) return
  const priceRule: AlertRule = {
    id: `${symbol.value}-price`,
    symbol: symbol.value,
    type: 'price_move',
    enabled: true,
  }
  watchStore.addRule(priceRule)
  if (Math.abs(snapshot.value.change_percent) >= 2) {
    const event: AlertEvent = {
      id: `${symbol.value}-${snapshot.value.timestamp}-price`,
      symbol: symbol.value,
      type: 'price_move',
      status: 'hit',
      title: `${symbol.value} 单日波动 ${formatMarketPercent(snapshot.value.change_percent)}`,
      read: false,
      created_at: new Date().toISOString(),
    }
    watchStore.addEvent(event)
  }
}

async function loadResearch() {
  loading.value = true
  error.value = ''
  try {
    const [snapshotResponse, candleResponse, newsResponse, overviewResponse] = await Promise.all([
      apiGet<MarketSnapshot>(`/api/stocks/${symbol.value}/snapshot`),
      apiGet<CandleSeries>(`/api/stocks/${symbol.value}/candles?interval=1d&limit=200`),
      apiGet<NewsFeedResponse>(`/api/stocks/${symbol.value}/news`),
      apiGet<MarketOverview>('/api/markets/overview'),
    ])
    snapshot.value = snapshotResponse
    candles.value = candleResponse
    newsFeed.value = newsResponse
    overview.value = overviewResponse
    forecast.value = await apiPost<Forecast5DResult>('/api/forecasts/5d', {
      symbol: symbol.value,
      interval: '1d',
      lookback: 260,
    })
    const job = await apiPost<BacktestResult>('/api/backtests', {
      symbol: symbol.value,
      strategy: 'trend_strength_volatility_filter',
      start_date: '2024-01-01T00:00:00Z',
      end_date: '2025-01-01T00:00:00Z',
      params: { trend_window: 80, strength_window: 20, vol_short: 10, vol_long: 30, max_vol_ratio: 1.15 },
    })
    backtest.value = await waitForBacktest(job.job_id)
    emitLocalAlerts()
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Failed to load research.'
  } finally {
    loading.value = false
  }
}

function addToWatch() {
  watchStore.addSymbol(symbol.value)
}

function addForecastAlert() {
  watchStore.addRule({
    id: `${symbol.value}-forecast`,
    symbol: symbol.value,
    type: 'forecast_shift',
    enabled: true,
  })
}

watch(symbol, () => {
  void loadResearch()
})

onMounted(() => {
  if (!systemStore.health) void systemStore.loadHealth()
  void loadResearch()
})
</script>

<template>
  <div class="research-layout">
    <div v-if="symbol.startsWith('US.')" class="panel empty-state">
      当前前端研究闭环默认仅支持港股与 A 股，美股入口已从主流程移除。
    </div>

    <template v-else>
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
          <div class="hero-actions">
            <button type="button" @click="addToWatch">{{ localeStore.t('research.watchlistAction') }}</button>
            <button type="button" class="secondary" @click="addForecastAlert">{{ localeStore.t('research.alertAction') }}</button>
          </div>
        </div>
        <div class="hero-stats">
          <MetricTile :label="localeStore.t('research.volume')" :value="compactNumber(snapshot.volume)" />
          <MetricTile :label="localeStore.t('research.turnover')" :value="compactNumber(snapshot.turnover)" />
          <MetricTile :label="localeStore.t('research.marketState')" :value="snapshot.market_state" />
        </div>
      </section>

      <div v-if="loading" class="panel loading-block">{{ localeStore.t('common.loading') }}</div>
      <div v-else-if="error" class="panel loading-block error">{{ error }}</div>

      <template v-else>
        <SectionPanel :title="localeStore.t('research.summary')" :subtitle="localeStore.t('common.whyWatch')">
          <div class="insight-grid">
            <MetricTile
              v-for="(item, index) in summaryBullets"
              :key="`summary-${index}`"
              :label="localeStore.t('research.scoreReasons')"
              :value="item"
            />
          </div>
        </SectionPanel>

        <div class="split-layout">
          <SectionPanel :title="localeStore.t('research.drivers')" subtitle="Drivers">
            <div class="pill-grid">
              <InsightPill v-for="tag in driverTags" :key="tag.label" :label="tag.label" :tone="tag.tone" />
            </div>
          </SectionPanel>
          <SectionPanel :title="localeStore.t('research.technicalTags')" subtitle="Structure">
            <div class="pill-grid">
              <InsightPill v-for="tag in technicalTags" :key="tag.label" :label="tag.label" :tone="tag.tone" />
            </div>
          </SectionPanel>
        </div>

        <div class="split-layout">
          <SectionPanel :title="localeStore.t('research.riskTags')" subtitle="Risk">
            <div class="pill-grid">
              <InsightPill v-for="tag in riskTags" :key="tag.label" :label="tag.label" :tone="tag.tone" />
            </div>
          </SectionPanel>
          <SectionPanel :title="localeStore.t('research.relativeStrength')" subtitle="Benchmark">
            <MetricTile
              :label="localeStore.t('research.relativeStrength')"
              :value="relativeStrength != null ? formatMarketPercent(relativeStrength) : '-'"
              :positive="relativeStrength != null ? relativeStrength >= 0 : null"
            />
          </SectionPanel>
        </div>

        <SectionPanel :title="localeStore.t('research.priceStructure')" :subtitle="localeStore.t('research.candlesVolume')">
          <div v-if="snapshot || candles" class="section-meta">
            <ProviderBadge
              v-if="snapshot"
              :label="buildLocalizedProviderBadgeLabel('snapshot', snapshot.source_status)"
              :status="snapshot.source_status"
            />
            <ProviderBadge
              v-if="candles"
              :label="buildLocalizedProviderBadgeLabel(`candles ${candles.interval}`, candles.source_status)"
              :status="candles.source_status"
            />
          </div>
          <CandleChart :series="candles" />
        </SectionPanel>

        <div class="split-layout">
          <SectionPanel :title="localeStore.t('research.relatedNews')" :subtitle="localeStore.t('research.attributedFeed')">
            <div v-if="newsFeed" class="section-meta">
              <ProviderBadge
                :label="buildLocalizedProviderBadgeLabel(newsFeed.provider, newsFeed.source_status)"
                :status="newsFeed.source_status"
              />
            </div>
            <div v-if="newsItems.length" class="news-grid">
              <NewsCard v-for="item in newsItems" :key="item.id" :item="item" />
            </div>
            <div v-else class="empty-state panel">{{ newsEmptyMessage }}</div>
          </SectionPanel>

          <SectionPanel :title="localeStore.t('research.forecast')" :subtitle="localeStore.t('research.forecastScenarios')">
            <div v-if="forecast" class="section-meta">
              <ProviderBadge
                :label="buildLocalizedProviderBadgeLabel(`forecast ${forecast.model_family}`, forecast.source_status)"
                :status="forecast.source_status"
              />
            </div>
            <div v-if="forecast" class="scenario-grid">
              <ScenarioCard v-for="scenario in forecast.scenarios" :key="scenario.label" :scenario="scenario" />
              <div class="forecast-summary panel">
                <div class="eyebrow">{{ localeStore.t('research.expectedBand') }}</div>
                <strong>{{ formatCurrency(forecast.expected_price_range[0]) }} - {{ formatCurrency(forecast.expected_price_range[1]) }}</strong>
                <p>{{ forecast.caveat }}</p>
              </div>
            </div>
          </SectionPanel>
        </div>

        <SectionPanel :title="localeStore.t('research.backtestSnapshot')" :subtitle="localeStore.t('research.institutionalDefault')">
          <div v-if="backtest?.metrics" class="backtest-grid">
            <MetricTile :label="localeStore.t('strategy.cumulative')" :value="formatPercent(backtest.metrics.cumulative_return)" />
            <MetricTile :label="localeStore.t('strategy.annualized')" :value="formatPercent(backtest.metrics.annualized_return)" />
            <MetricTile :label="localeStore.t('strategy.sharpe')" :value="backtest.metrics.sharpe_ratio.toFixed(2)" />
            <MetricTile :label="localeStore.t('strategy.maxDrawdown')" :value="formatPercent(backtest.metrics.max_drawdown)" />
          </div>
        </SectionPanel>
      </template>
    </template>
  </div>
</template>

<style scoped>
.research-layout,
.split-layout,
.news-grid,
.scenario-grid,
.backtest-grid,
.insight-grid,
.pill-grid {
  display: grid;
  gap: 20px;
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
.backtest-grid,
.insight-grid {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.split-layout {
  grid-template-columns: 1fr 1fr;
}

.pill-grid {
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
}

.hero-actions {
  display: flex;
  gap: 12px;
  margin-top: 18px;
}

.hero-actions button {
  border: none;
  border-radius: 14px;
  padding: 12px 16px;
  cursor: pointer;
  background: linear-gradient(90deg, var(--accent), var(--accent-2));
  color: #041019;
  font-weight: 700;
}

.hero-actions .secondary {
  background: transparent;
  color: var(--text);
  border: 1px solid var(--border);
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
  .backtest-grid,
  .insight-grid {
    grid-template-columns: 1fr;
  }
}
</style>
