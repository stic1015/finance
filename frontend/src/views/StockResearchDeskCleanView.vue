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

type PillTone = 'neutral' | 'positive' | 'negative'

const route = useRoute()
const localeStore = useLocaleStore()
const systemStore = useSystemStore()
const watchStore = useWatchStore()
const symbol = computed(() => String(route.params.symbol ?? 'HK.00700'))

const snapshot = ref<MarketSnapshot | null>(null)
const candles = ref<CandleSeries | null>(null)
const newsFeed = ref<NewsFeedResponse | null>(null)
const marketBriefs = ref<NewsFeedResponse | null>(null)
const forecast = ref<Forecast5DResult | null>(null)
const backtest = ref<BacktestResult | null>(null)
const overview = ref<MarketOverview | null>(null)
const loading = ref(false)
const error = ref('')
const analysisInterval = ref<'1d' | '1h' | '30m' | '15m'>('30m')

const newsItems = computed(() => newsFeed.value?.items ?? [])
const newsEmptyMessage = computed(() =>
  newsFeed.value ? getLocalizedNewsEmptyMessage(newsFeed.value) : localeStore.t('common.noAttributedNews'),
)

const summaryBullets = computed(() => {
  if (!snapshot.value || !forecast.value) return []
  const items: string[] = []
  if (snapshot.value.change_percent > 2) items.push(`${localeStore.t('research.intradayMove')} ${formatMarketPercent(snapshot.value.change_percent)}`)
  if (forecast.value.scenarios.length) {
    const leader = [...forecast.value.scenarios].sort((a, b) => b.probability - a.probability)[0]
    items.push(`${localeStore.t('research.dominantScenario')} ${leader.label}`)
  }
  if (newsItems.value.length) items.push(`${localeStore.t('research.newsClues')} ${newsItems.value.length}`)
  if (snapshot.value.source_status !== 'live') items.push(localeStore.t('research.restrictedRealtime'))
  return items
})

const driverTags = computed<{ label: string; tone: PillTone }[]>(() => {
  if (!snapshot.value || !forecast.value) return []
  const leader = [...forecast.value.scenarios].sort((a, b) => b.probability - a.probability)[0]
  return [
    { label: snapshot.value.change_percent >= 0 ? localeStore.t('research.strongerThanYesterday') : localeStore.t('research.weakerThanYesterday'), tone: snapshot.value.change_percent >= 0 ? 'positive' : 'negative' },
    { label: `${localeStore.t('research.volume')} ${compactNumber(snapshot.value.volume)}`, tone: 'neutral' },
    { label: `${localeStore.t('research.dominantScenario')} ${leader.label}`, tone: 'neutral' },
  ]
})

const technicalTags = computed<{ label: string; tone: PillTone }[]>(() => {
  if (!candles.value?.points.length) return []
  const latest = candles.value.points.at(-1)!
  const shortAverage = candles.value.points.slice(-20).reduce((sum, point) => sum + point.close, 0) / Math.min(candles.value.points.length, 20)
  return [
    { label: latest.close >= shortAverage ? localeStore.t('research.above20d') : localeStore.t('research.below20d'), tone: latest.close >= shortAverage ? 'positive' : 'negative' },
    { label: latest.close >= latest.open ? localeStore.t('research.daylineStrong') : localeStore.t('research.daylineWeak'), tone: latest.close >= latest.open ? 'positive' : 'negative' },
  ]
})

const riskTags = computed<{ label: string; tone: PillTone }[]>(() => {
  const tags: { label: string; tone: PillTone }[] = []
  if (snapshot.value?.source_status !== 'live') tags.push({ label: localeStore.t('common.restricted'), tone: 'negative' })
  if (newsFeed.value?.source_status === 'unavailable') tags.push({ label: localeStore.t('research.newsSourceUnavailable'), tone: 'negative' })
  if (forecast.value && forecast.value.scenarios.some((item) => item.label === 'bearish' && item.probability > 0.4)) {
    tags.push({ label: localeStore.t('research.bearishRisk'), tone: 'negative' })
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
const leadScenario = computed(() =>
  forecast.value?.scenarios.length
    ? [...forecast.value.scenarios].sort((a, b) => b.probability - a.probability)[0]
    : null,
)
const thesisHeadline = computed(() => {
  if (!snapshot.value || !leadScenario.value) return ''
  if (snapshot.value.change_percent >= 2 && leadScenario.value.label === 'bullish') {
    return localeStore.locale === 'zh-CN' ? '强势延续，适合继续跟踪确认' : 'Momentum still has support'
  }
  if (snapshot.value.change_percent <= -2 || leadScenario.value.label === 'bearish') {
    return localeStore.locale === 'zh-CN' ? '风险抬升，先看保护位再决定' : 'Risk is rising before conviction'
  }
  return localeStore.locale === 'zh-CN' ? '结论未定，等待更多证据闭环' : 'Neutral setup, waiting for confirmation'
})
const thesisSummary = computed(() => {
  if (!snapshot.value) return ''
  if (snapshot.value.source_status !== 'live') {
    return localeStore.locale === 'zh-CN'
      ? '当前不是实时行情，先把它当成研究输入而不是交易指令。'
      : 'Feed is not fully live, so treat this as research input rather than execution guidance.'
  }
  return localeStore.locale === 'zh-CN'
    ? '先用价格结构和主导情景形成判断，再决定是否加入观察、设置预警或进入策略验证。'
    : 'Build conviction from price structure and scenario leadership before watching, alerting, or validating.'
})
const evidenceChain = computed(() => [
  ...summaryBullets.value,
  ...(forecast.value?.rationale ?? []),
].slice(0, 5))
const evidenceFeed = computed(() => (newsItems.value.length ? newsItems.value : marketBriefs.value?.items ?? []))

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
  const priceRule: AlertRule = { id: `${symbol.value}-price`, symbol: symbol.value, type: 'price_move', enabled: true }
  watchStore.addRule(priceRule)
  if (Math.abs(snapshot.value.change_percent) >= 2) {
    const event: AlertEvent = {
      id: `${symbol.value}-${snapshot.value.timestamp}-price`,
      symbol: symbol.value,
      type: 'price_move',
      status: 'hit',
      title: `${symbol.value} ${localeStore.t('research.priceMoveAlert')} ${formatMarketPercent(snapshot.value.change_percent)}`,
      read: false,
      created_at: new Date().toISOString(),
    }
    watchStore.addEvent(event)
  }
  if (newsItems.value.length) {
    watchStore.addEvent({
      id: `${symbol.value}-${newsItems.value[0].id}-news`,
      symbol: symbol.value,
      type: 'news_ready',
      status: 'hit',
      title: `${symbol.value} ${localeStore.t('research.newsAlert')}`,
      read: false,
      created_at: new Date().toISOString(),
    })
  }
}

async function loadResearch() {
  loading.value = true
  error.value = ''
  try {
    const [snapshotResponse, candleResponse, newsResponse, overviewResponse] = await Promise.all([
      apiGet<MarketSnapshot>(`/api/stocks/${symbol.value}/snapshot`),
      apiGet<CandleSeries>(`/api/stocks/${symbol.value}/candles?interval=${analysisInterval.value}&limit=200`),
      apiGet<NewsFeedResponse>(`/api/stocks/${symbol.value}/news`),
      apiGet<MarketOverview>('/api/markets/overview'),
    ])
    snapshot.value = snapshotResponse
    candles.value = candleResponse
    newsFeed.value = newsResponse
    overview.value = overviewResponse
    marketBriefs.value = await apiGet<NewsFeedResponse>('/api/markets/briefs')
    forecast.value = await apiPost<Forecast5DResult>('/api/forecasts/5d', {
      symbol: symbol.value,
      interval: analysisInterval.value,
      lookback: 260,
    })
    const job = await apiPost<BacktestResult>('/api/backtests', {
      symbol: symbol.value,
      strategy: 'trend_strength_volatility_filter',
      interval: analysisInterval.value,
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
watch(analysisInterval, () => {
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
      {{ localeStore.t('research.usRemoved') }}
    </div>

    <template v-else>
      <section class="hero panel" v-if="snapshot">
        <div class="hero-copy">
          <div class="eyebrow">{{ snapshot.symbol }}</div>
          <h2>{{ snapshot.display_name }}</h2>
          <p class="hero-thesis">{{ thesisHeadline }}</p>
          <p class="hero-summary">{{ thesisSummary }}</p>
          <div class="hero-price-row">
            <strong>{{ formatCurrency(snapshot.price) }}</strong>
            <span :class="snapshot.change_percent >= 0 ? 'status-positive' : 'status-negative'">
              {{ formatMarketPercent(snapshot.change_percent) }}
            </span>
          </div>
          <div class="hero-badges">
            <ProviderBadge :label="buildLocalizedProviderBadgeLabel('snapshot', snapshot.source_status)" :status="snapshot.source_status" />
            <ProviderBadge
              v-if="forecast"
              :label="buildLocalizedProviderBadgeLabel(`forecast ${forecast.model_family}`, forecast.source_status)"
              :status="forecast.source_status"
            />
          </div>
          <div class="hero-actions">
            <button type="button" @click="addToWatch">{{ localeStore.t('research.watchlistAction') }}</button>
            <button type="button" class="secondary" @click="addForecastAlert">{{ localeStore.t('research.alertAction') }}</button>
            <RouterLink class="hero-link" to="/strategy-lab">
              {{ localeStore.locale === 'zh-CN' ? '进入策略实验室' : 'Open Strategy Lab' }}
            </RouterLink>
            <label class="interval-select">
              <span>{{ localeStore.locale === 'zh-CN' ? '周期' : 'Interval' }}</span>
              <select v-model="analysisInterval">
                <option value="1d">1d</option>
                <option value="1h">1h</option>
                <option value="30m">30m</option>
                <option value="15m">15m</option>
              </select>
            </label>
          </div>
        </div>
        <div class="hero-sidebar">
          <div class="hero-stats">
            <MetricTile :label="localeStore.t('research.volume')" :value="compactNumber(snapshot.volume)" />
            <MetricTile :label="localeStore.t('research.turnover')" :value="compactNumber(snapshot.turnover)" />
            <MetricTile :label="localeStore.t('research.marketState')" :value="snapshot.market_state" />
            <MetricTile
              :label="localeStore.t('research.relativeStrength')"
              :value="relativeStrength != null ? formatMarketPercent(relativeStrength) : '-'"
              :positive="relativeStrength != null ? relativeStrength >= 0 : null"
            />
          </div>
          <div class="hero-evidence glass-line">
            <div class="eyebrow">{{ localeStore.locale === 'zh-CN' ? '主证据链' : 'Evidence Chain' }}</div>
            <ul>
              <li v-for="(item, index) in evidenceChain" :key="`evidence-${index}`">{{ item }}</li>
            </ul>
          </div>
        </div>
      </section>

      <div v-if="loading" class="panel empty-shell">{{ localeStore.t('common.loading') }}</div>
      <div v-else-if="error" class="panel empty-shell error">{{ error }}</div>

      <template v-else>
        <div class="research-canvas">
          <div class="main-column">
            <SectionPanel :title="localeStore.t('research.priceStructure')" :subtitle="localeStore.t('research.candlesVolume')">
              <div v-if="snapshot || candles" class="section-meta">
                <ProviderBadge v-if="snapshot" :label="buildLocalizedProviderBadgeLabel('snapshot', snapshot.source_status)" :status="snapshot.source_status" />
                <ProviderBadge v-if="candles" :label="buildLocalizedProviderBadgeLabel(`candles ${candles.interval}`, candles.source_status)" :status="candles.source_status" />
              </div>
              <CandleChart :series="candles" />
            </SectionPanel>

            <div class="matrix-grid">
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
              <SectionPanel :title="localeStore.t('research.riskTags')" subtitle="Risk">
                <div class="pill-grid">
                  <InsightPill v-for="tag in riskTags" :key="tag.label" :label="tag.label" :tone="tag.tone" />
                </div>
              </SectionPanel>
            </div>

            <SectionPanel :title="localeStore.t('research.relatedNews')" :subtitle="localeStore.t('research.attributedFeed')">
              <div v-if="newsFeed" class="section-meta">
                <ProviderBadge :label="buildLocalizedProviderBadgeLabel(newsFeed.provider, newsFeed.source_status)" :status="newsFeed.source_status" />
              </div>
              <div v-if="evidenceFeed.length" class="news-grid">
                <NewsCard v-for="item in evidenceFeed.slice(0, 4)" :key="item.id" :item="item" />
              </div>
              <div v-else class="evidence-empty">{{ newsEmptyMessage }}</div>
            </SectionPanel>
          </div>

          <aside class="side-column">
            <SectionPanel :title="localeStore.t('research.forecast')" :subtitle="localeStore.t('research.forecastScenarios')">
              <div v-if="forecast" class="scenario-grid">
                <ScenarioCard v-for="scenario in forecast.scenarios" :key="scenario.label" :scenario="scenario" />
                <div class="forecast-summary glass-line">
                  <div class="eyebrow">{{ localeStore.t('research.expectedBand') }}</div>
                  <strong>{{ formatCurrency(forecast.expected_price_range[0]) }} - {{ formatCurrency(forecast.expected_price_range[1]) }}</strong>
                  <p>{{ forecast.caveat }}</p>
                </div>
              </div>
            </SectionPanel>

            <SectionPanel :title="localeStore.t('research.backtestSnapshot')" :subtitle="localeStore.t('research.institutionalDefault')">
              <div v-if="backtest?.metrics" class="backtest-grid">
                <MetricTile :label="localeStore.t('strategy.cumulative')" :value="formatPercent(backtest.metrics.cumulative_return)" />
                <MetricTile :label="localeStore.t('strategy.annualized')" :value="formatPercent(backtest.metrics.annualized_return)" />
                <MetricTile :label="localeStore.t('strategy.sharpe')" :value="backtest.metrics.sharpe_ratio.toFixed(2)" />
                <MetricTile :label="localeStore.t('strategy.maxDrawdown')" :value="formatPercent(backtest.metrics.max_drawdown)" />
              </div>
              <div v-else class="evidence-empty">
                {{ localeStore.locale === 'zh-CN' ? '回测快照尚未准备好。' : 'Backtest snapshot is not ready yet.' }}
              </div>
            </SectionPanel>

            <SectionPanel :title="localeStore.locale === 'zh-CN' ? '市场上下文' : 'Market Context'" :subtitle="localeStore.locale === 'zh-CN' ? '相对市场再看一次' : 'Re-check relative positioning'">
              <div class="context-stack">
                <MetricTile
                  :label="localeStore.t('research.relativeStrength')"
                  :value="relativeStrength != null ? formatMarketPercent(relativeStrength) : '-'"
                  :positive="relativeStrength != null ? relativeStrength >= 0 : null"
                />
                <div class="context-note glass-line">
                  <div class="eyebrow">{{ localeStore.locale === 'zh-CN' ? '主导情景' : 'Lead Scenario' }}</div>
                  <strong>{{ leadScenario ? leadScenario.label : '-' }}</strong>
                  <p>
                    {{
                      localeStore.locale === 'zh-CN'
                        ? '如果这里和价格结构方向不一致，优先相信结构，再等待情景修正。'
                        : 'If this disagrees with the chart structure, trust the structure first and wait for scenario alignment.'
                    }}
                  </p>
                </div>
              </div>
            </SectionPanel>
          </aside>
        </div>
      </template>
    </template>
  </div>
</template>

<style scoped>
.research-layout,
.news-grid,
.scenario-grid,
.backtest-grid,
.pill-grid,
.matrix-grid,
.research-canvas,
.context-stack {
  display: grid;
  gap: 20px;
}

.hero {
  display: grid;
  grid-template-columns: minmax(0, 1.15fr) minmax(360px, 0.95fr);
  gap: 24px;
  padding: 28px 28px 26px;
}

.hero h2 {
  margin: 8px 0 0;
  font-size: clamp(2.2rem, 3vw, 3.6rem);
  font-family: 'Chakra Petch', sans-serif;
  line-height: 0.94;
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

.hero-copy {
  display: grid;
  gap: 14px;
}

.hero-thesis {
  margin: 0;
  font-size: 1.12rem;
  color: var(--text);
}

.hero-summary,
.forecast-summary p,
.context-note p {
  margin: 0;
  color: var(--text-secondary);
  line-height: 1.6;
}

.hero-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.hero-sidebar,
.hero-evidence {
  display: grid;
  gap: 16px;
}

.hero-stats,
.backtest-grid,
.matrix-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.pill-grid {
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.hero-actions button,
.hero-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: none;
  border-radius: 14px;
  padding: 12px 16px;
  cursor: pointer;
  background: linear-gradient(135deg, var(--accent), var(--accent-2));
  color: #041019;
  font-weight: 700;
}

.hero-actions .secondary {
  background: transparent;
  color: var(--text);
  border: 1px solid var(--border-subtle);
}

.hero-link {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--border-subtle);
  color: var(--text);
}

.interval-select {
  display: inline-grid;
  gap: 6px;
  color: var(--text-secondary);
  font-size: 0.84rem;
}

.interval-select select {
  min-height: 40px;
  padding: 8px 12px;
  border-radius: 10px;
  border: 1px solid var(--border-subtle);
  background: rgba(4, 10, 16, 0.75);
  color: var(--text);
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

.research-canvas {
  grid-template-columns: minmax(0, 1.45fr) 360px;
  align-items: start;
}

.section-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.evidence-empty {
  padding: 16px;
  border-radius: 18px;
  border: 1px dashed var(--border-subtle);
  color: var(--text-secondary);
  background: rgba(255, 255, 255, 0.02);
}

.context-note,
.hero-evidence {
  padding: 16px;
}

.hero-evidence ul {
  margin: 0;
  padding-left: 18px;
  color: var(--text-secondary);
  display: grid;
  gap: 10px;
}

@media (max-width: 1200px) {
  .hero,
  .research-canvas,
  .hero-stats,
  .backtest-grid,
  .matrix-grid {
    grid-template-columns: 1fr;
  }
}
</style>
