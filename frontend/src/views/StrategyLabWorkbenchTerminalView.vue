<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'

import { apiGet, apiPost } from '@/api/client'
import CompareRunsTable from '@/components/CompareRunsTable.vue'
import MetricTile from '@/components/MetricTile.vue'
import MonthlyHeatmap from '@/components/MonthlyHeatmap.vue'
import PerformanceTradeChartExplained from '@/components/PerformanceTradeChartExplained.vue'
import ResearchStrategyFormClean from '@/components/ResearchStrategyFormClean.vue'
import SectionPanel from '@/components/SectionPanel.vue'
import TradeExecutionTableExplained from '@/components/TradeExecutionTableExplained.vue'
import { FALLBACK_STRATEGIES } from '@/constants/strategies'
import { useLocaleStore } from '@/stores/locale'
import type { BacktestResult, MonthlyTradeSummary, StrategyDefinition } from '@/types'
import { formatCurrency, formatPercent } from '@/utils/format'
import { translateTradeAction } from '@/utils/presentation'

const localeStore = useLocaleStore()
const latestRun = ref<BacktestResult | null>(null)
const runHistory = ref<BacktestResult[]>([])
const strategies = ref<StrategyDefinition[]>([])
const selectedMonth = ref<string | null>(null)
const loading = ref(false)
const error = ref('')

const selectedStrategy = computed(() => {
  return (
    strategies.value.find((item) => item.name === latestRun.value?.strategy) ??
    strategies.value[0] ??
    FALLBACK_STRATEGIES[0]
  )
})

const monthlyTradeSummaries = computed(() => latestRun.value?.monthly_trade_summaries ?? [])
const activeMonth = computed(
  () => monthlyTradeSummaries.value.find((item) => item.month === selectedMonth.value) ?? monthlyTradeSummaries.value[0] ?? null,
)
const visibleTradeRows = computed(() => {
  if (!latestRun.value) return []
  if (!selectedMonth.value) return latestRun.value.trade_log
  return latestRun.value.trade_log.filter((row) => row.month === selectedMonth.value)
})
const latestMetrics = computed(() => latestRun.value?.metrics ?? null)
const runHeadline = computed(() => {
  if (!latestMetrics.value || !latestRun.value) {
    return localeStore.locale === 'zh-CN'
      ? '先配置模板并运行一轮回测，再进入解释和比较。'
      : 'Configure a template and run a backtest before moving into explanation and comparison.'
  }
  if ((latestRun.value.excess_return ?? 0) > 0) {
    return localeStore.locale === 'zh-CN'
      ? '当前结果跑赢基准，先看交易点和月度解释是否一致。'
      : 'This run is ahead of the benchmark. Check whether trade markers and monthly explanations agree.'
  }
  return localeStore.locale === 'zh-CN'
    ? '当前结果还不够强，优先复盘回撤和月度交易节奏。'
    : 'This run is still fragile. Review drawdown and monthly trade rhythm first.'
})
const activeMonthNote = computed(() => {
  if (!activeMonth.value) {
    return localeStore.locale === 'zh-CN'
      ? '先看总曲线，再按月份切入解释。'
      : 'Start from the full equity curve, then drill down by month.'
  }
  return localeStore.locale === 'zh-CN'
    ? `${activeMonth.value.month} 以 ${dominantAction(activeMonth.value)} 为主，交易 ${activeMonth.value.trade_count} 次。`
    : `${activeMonth.value.month} was led by ${dominantAction(activeMonth.value)} with ${activeMonth.value.trade_count} trades.`
})

async function loadStrategies() {
  try {
    strategies.value = await apiGet<StrategyDefinition[]>('/api/backtests/strategies')
  } catch {
    strategies.value = FALLBACK_STRATEGIES
  }
}

async function submitBacktest(payload: {
  symbol: string
  strategy: string
  start_date: string
  end_date: string
  params: Record<string, number>
}) {
  loading.value = true
  error.value = ''
  try {
    const queued = await apiPost<BacktestResult>('/api/backtests', payload)
    let result = await apiGet<BacktestResult>(`/api/backtests/${queued.job_id}`)
    for (let attempt = 0; attempt < 8 && result.status === 'running'; attempt += 1) {
      await new Promise((resolve) => window.setTimeout(resolve, 1200))
      result = await apiGet<BacktestResult>(`/api/backtests/${queued.job_id}`)
    }
    latestRun.value = result
    runHistory.value = [result, ...runHistory.value.filter((item) => item.job_id !== result.job_id)].slice(0, 6)
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Run backtest failed.'
  } finally {
    loading.value = false
  }
}

function selectMonth(month: string | null) {
  selectedMonth.value = month
}

function dominantAction(summary: MonthlyTradeSummary) {
  const counts = [
    { action: 'buy', value: summary.buy_count },
    { action: 'sell', value: summary.sell_count },
    { action: 'rebalance', value: summary.rebalance_count },
  ].sort((a, b) => b.value - a.value)
  return counts[0].value > 0 ? translateTradeAction(counts[0].action, localeStore.locale) : '-'
}

watch(
  () => latestRun.value?.job_id,
  () => {
    selectedMonth.value = latestRun.value?.monthly_trade_summaries.at(-1)?.month ?? null
  },
)

onMounted(() => {
  void loadStrategies()
})
</script>

<template>
  <div class="strategy-layout">
    <section class="hero panel">
      <div class="hero-copy">
        <div class="eyebrow">{{ localeStore.t('strategy.eyebrow') }}</div>
        <h2>{{ localeStore.t('strategy.runResults') }}</h2>
        <p>{{ localeStore.t('strategy.description') }}</p>
        <p class="hero-note">{{ runHeadline }}</p>
      </div>
      <div class="hero-metrics">
        <MetricTile
          :label="localeStore.locale === 'zh-CN' ? '当前模板' : 'Active Template'"
          :value="selectedStrategy.label"
        />
        <MetricTile
          :label="localeStore.locale === 'zh-CN' ? '已选择月份' : 'Focus Month'"
          :value="selectedMonth ?? (localeStore.locale === 'zh-CN' ? '全部' : 'All')"
        />
      </div>
    </section>

    <div class="lab-grid">
      <aside class="lab-sidebar">
        <SectionPanel :title="localeStore.t('strategy.controls')" :subtitle="localeStore.t('strategy.templateAndParams')">
          <ResearchStrategyFormClean :strategies="strategies.length ? strategies : FALLBACK_STRATEGIES" @submit="submitBacktest" />
        </SectionPanel>

        <SectionPanel :title="localeStore.locale === 'zh-CN' ? '策略摘要' : 'Strategy Summary'" :subtitle="localeStore.t('strategy.performanceAndNotes')">
          <div class="strategy-summary glass-line">
            <div class="eyebrow">{{ selectedStrategy.category }}</div>
            <strong>{{ selectedStrategy.label }}</strong>
            <p>{{ selectedStrategy.description }}</p>
            <p class="section-note">{{ localeStore.t('strategy.logicSummary') }}: {{ selectedStrategy.logic_summary }}</p>
            <p class="section-note">{{ localeStore.t('strategy.styleTags') }}: {{ selectedStrategy.style_tags.join(' / ') }}</p>
            <p class="section-note">{{ localeStore.t('strategy.marketScope') }}: {{ selectedStrategy.market_scope.join(' / ') }}</p>
          </div>
        </SectionPanel>
      </aside>

      <div class="lab-results">
        <div v-if="loading" class="panel empty-shell">{{ localeStore.t('common.loading') }}</div>
        <div v-else-if="error" class="panel empty-shell error">{{ error }}</div>
        <template v-else-if="latestRun && latestMetrics">
          <section class="results-hero panel">
            <div class="results-copy">
              <div class="eyebrow">{{ latestRun.symbol }}</div>
              <h3>{{ selectedStrategy.label }}</h3>
              <p>{{ runHeadline }}</p>
            </div>
            <div class="results-status glass-line">
              <div class="eyebrow">{{ localeStore.locale === 'zh-CN' ? '结果状态' : 'Run Status' }}</div>
              <strong>{{ latestRun.status }}</strong>
              <span class="mono">{{ latestRun.job_id }}</span>
            </div>
          </section>

          <div class="metrics-grid">
            <MetricTile :label="localeStore.t('strategy.cumulative')" :value="formatPercent(latestMetrics.cumulative_return)" />
            <MetricTile :label="localeStore.t('strategy.annualized')" :value="formatPercent(latestMetrics.annualized_return)" />
            <MetricTile :label="localeStore.t('strategy.sharpe')" :value="latestMetrics.sharpe_ratio.toFixed(2)" />
            <MetricTile :label="localeStore.t('strategy.maxDrawdown')" :value="formatPercent(latestMetrics.max_drawdown)" />
            <MetricTile :label="localeStore.t('strategy.winRate')" :value="formatPercent(latestMetrics.win_rate)" />
            <MetricTile :label="localeStore.t('strategy.tradeCount')" :value="String(latestMetrics.trade_count)" />
            <MetricTile :label="localeStore.t('strategy.excessReturn')" :value="latestRun.excess_return != null ? formatPercent(latestRun.excess_return) : '-'" />
          </div>

          <SectionPanel :title="localeStore.t('strategy.tradeMarkers')" :subtitle="localeStore.t('strategy.tradeFocusHint')">
            <div class="trade-focus-row">
              <button type="button" class="interactive-chip" :class="{ active: !selectedMonth }" @click="selectMonth(null)">
                {{ localeStore.t('strategy.allTrades') }}
              </button>
              <button
                v-for="summary in monthlyTradeSummaries"
                :key="summary.month"
                type="button"
                class="interactive-chip"
                :class="{ active: summary.month === selectedMonth }"
                @click="selectMonth(summary.month)"
              >
                {{ summary.month }}
              </button>
            </div>
            <PerformanceTradeChartExplained
              :points="latestRun.equity_curve"
              :trades="latestRun.trade_log"
              :selected-month="selectedMonth"
            />
          </SectionPanel>

          <SectionPanel :title="localeStore.t('strategy.monthlyExplainer')" :subtitle="localeStore.t('strategy.monthlyHeatmap')">
            <div class="monthly-summary glass-line">
              <div class="eyebrow">{{ localeStore.locale === 'zh-CN' ? '月份解读' : 'Monthly Read' }}</div>
              <p>{{ activeMonthNote }}</p>
            </div>
            <MonthlyHeatmap :points="latestRun.monthly_returns" />
            <div class="monthly-grid">
              <button
                v-for="summary in monthlyTradeSummaries"
                :key="summary.month"
                type="button"
                class="month-card panel"
                :class="{ active: summary.month === selectedMonth }"
                @click="selectMonth(summary.month)"
              >
                <div class="month-head">
                  <div class="eyebrow">{{ summary.month }}</div>
                  <strong :class="summary.return_rate >= 0 ? 'status-positive' : 'status-negative'">
                    {{ formatPercent(summary.return_rate) }}
                  </strong>
                </div>
                <div class="month-meta">
                  <span>{{ localeStore.t('strategy.benchmarkReturn') }} {{ formatPercent(summary.benchmark_return) }}</span>
                  <span>{{ localeStore.t('strategy.tradeCount') }} {{ summary.trade_count }}</span>
                  <span>{{ localeStore.t('strategy.tradeMarkers') }} {{ dominantAction(summary) }}</span>
                </div>
              </button>
            </div>
            <div v-if="activeMonth" class="active-month-grid">
              <MetricTile :label="localeStore.t('strategy.startEquity')" :value="formatCurrency(activeMonth.start_equity)" />
              <MetricTile :label="localeStore.t('strategy.endEquity')" :value="formatCurrency(activeMonth.end_equity)" />
              <MetricTile :label="localeStore.t('strategy.tradeCount')" :value="String(activeMonth.trade_count)" />
              <MetricTile :label="localeStore.t('strategy.benchmarkReturn')" :value="formatPercent(activeMonth.benchmark_return)" />
            </div>
          </SectionPanel>

          <SectionPanel
            :title="localeStore.t('strategy.trades')"
            :subtitle="selectedMonth ? `${localeStore.t('strategy.filteredTrades')}: ${selectedMonth}` : localeStore.t('strategy.allTrades')"
          >
            <TradeExecutionTableExplained :rows="visibleTradeRows" :empty-label="localeStore.t('strategy.noTradesForMonth')" />
          </SectionPanel>

          <SectionPanel :title="localeStore.t('strategy.compare')" :subtitle="localeStore.locale === 'zh-CN' ? '最近运行比较' : 'Recent run comparison'">
            <CompareRunsTable :runs="runHistory" />
          </SectionPanel>
        </template>
        <div v-else class="panel empty-shell">{{ localeStore.t('strategy.chooseToRun') }}</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.strategy-layout,
.lab-grid,
.metrics-grid,
.monthly-grid,
.active-month-grid,
.lab-results {
  display: grid;
  gap: 20px;
}

.hero {
  display: grid;
  grid-template-columns: minmax(0, 1.1fr) 360px;
  gap: 24px;
  padding: 24px 26px;
}

.hero h2 {
  margin: 8px 0 10px;
  font-size: clamp(2rem, 2.8vw, 3rem);
  font-family: 'Chakra Petch', sans-serif;
  line-height: 0.95;
}

.hero p,
.monthly-summary p,
.results-copy p {
  max-width: 720px;
  margin: 0;
  color: var(--text-secondary);
  line-height: 1.6;
}

.hero-copy {
  display: grid;
  gap: 10px;
}

.hero-note {
  font-size: 1.02rem;
  color: var(--text);
}

.hero-metrics {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.strategy-summary {
  padding: 18px;
}

.strategy-summary strong {
  display: block;
  margin: 10px 0 8px;
  font-size: 1.5rem;
  font-family: 'Chakra Petch', sans-serif;
}

.strategy-summary p,
.section-note {
  margin: 0 0 10px;
  color: var(--text-secondary);
}

.lab-grid {
  grid-template-columns: 380px minmax(0, 1fr);
  align-items: start;
}

.lab-sidebar {
  display: grid;
  gap: 20px;
  position: sticky;
  top: 24px;
}

.metrics-grid {
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.results-hero {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 260px;
  gap: 18px;
  padding: 22px;
}

.results-copy {
  display: grid;
  gap: 10px;
}

.results-copy h3,
.results-status strong {
  margin: 0;
  font-size: 1.7rem;
  font-family: 'Chakra Petch', sans-serif;
}

.results-status,
.monthly-summary {
  padding: 16px;
}

.results-status {
  display: grid;
  gap: 10px;
  align-content: start;
}

.trade-focus-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.month-card.active {
  border-color: var(--border-strong);
  box-shadow: inset 0 0 0 1px rgba(55, 214, 255, 0.18);
}

.monthly-grid {
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
}

.month-card {
  padding: 16px;
  border-radius: 20px;
  text-align: left;
  cursor: pointer;
}

.month-head,
.month-meta {
  display: grid;
  gap: 8px;
}

.month-head strong {
  font-size: 1.35rem;
}

.month-meta {
  color: var(--text-secondary);
  font-size: 0.92rem;
}

.active-month-grid {
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

@media (max-width: 1200px) {
  .hero,
  .lab-grid,
  .metrics-grid,
  .active-month-grid,
  .results-hero {
    grid-template-columns: 1fr;
  }

  .lab-sidebar {
    position: static;
  }
}

@media (max-width: 860px) {
  .hero-metrics,
  .monthly-grid {
    grid-template-columns: 1fr;
  }
}
</style>
