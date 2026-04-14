<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import { apiGet, apiPost } from '@/api/client'
import CompareRunsTable from '@/components/CompareRunsTable.vue'
import MetricTile from '@/components/MetricTile.vue'
import MonthlyHeatmap from '@/components/MonthlyHeatmap.vue'
import PerformanceChart from '@/components/PerformanceChart.vue'
import ResearchStrategyFormClean from '@/components/ResearchStrategyFormClean.vue'
import SectionPanel from '@/components/SectionPanel.vue'
import TradeLogTable from '@/components/TradeLogTable.vue'
import { FALLBACK_STRATEGIES, localizeStrategies } from '@/constants/strategies'
import { useLocaleStore } from '@/stores/locale'
import type { BacktestResult, StrategyDefinition } from '@/types'
import { formatPercent } from '@/utils/format'

const localeStore = useLocaleStore()
const latestRun = ref<BacktestResult | null>(null)
const runHistory = ref<BacktestResult[]>([])
const strategies = ref<StrategyDefinition[]>([])
const loading = ref(false)
const error = ref('')
const localizedStrategies = computed(() =>
  localizeStrategies(strategies.value.length ? strategies.value : FALLBACK_STRATEGIES, localeStore.locale),
)

const selectedStrategy = computed(() => {
  return (
    localizedStrategies.value.find((item) => item.name === latestRun.value?.strategy) ??
    localizedStrategies.value[0] ??
    localizeStrategies([FALLBACK_STRATEGIES[0]], localeStore.locale)[0]
  )
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
  interval: string
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

onMounted(() => {
  void loadStrategies()
})
</script>

<template>
  <div class="strategy-layout">
    <section class="hero panel">
      <div>
        <div class="eyebrow">{{ localeStore.t('strategy.eyebrow') }}</div>
        <h2>{{ localeStore.t('strategy.title') }}</h2>
        <p>{{ localeStore.t('strategy.description') }}</p>
      </div>
    </section>

    <div class="lab-grid">
      <SectionPanel :title="localeStore.t('strategy.controls')" :subtitle="localeStore.t('strategy.templateAndParams')">
        <ResearchStrategyFormClean :strategies="localizedStrategies" @submit="submitBacktest" />
      </SectionPanel>

      <SectionPanel :title="localeStore.t('strategy.runResults')" :subtitle="localeStore.t('strategy.performanceAndNotes')">
        <div class="strategy-summary panel">
          <div class="eyebrow">{{ selectedStrategy.category }}</div>
          <strong>{{ selectedStrategy.label }}</strong>
          <p>{{ selectedStrategy.description }}</p>
          <p class="section-note">{{ localeStore.t('strategy.logicSummary') }}: {{ selectedStrategy.logic_summary }}</p>
          <p class="section-note">{{ localeStore.t('strategy.styleTags') }}: {{ selectedStrategy.style_tags.join(' / ') }}</p>
          <p class="section-note">{{ localeStore.t('strategy.marketScope') }}: {{ selectedStrategy.market_scope.join(' / ') }}</p>
        </div>

        <div v-if="loading" class="panel empty-state">{{ localeStore.t('common.loading') }}</div>
        <div v-else-if="error" class="panel empty-state error">{{ error }}</div>
        <div v-else-if="latestRun?.metrics" class="results-grid">
          <div class="metrics-grid">
            <MetricTile :label="localeStore.t('strategy.cumulative')" :value="formatPercent(latestRun.metrics.cumulative_return)" />
            <MetricTile :label="localeStore.t('strategy.annualized')" :value="formatPercent(latestRun.metrics.annualized_return)" />
            <MetricTile :label="localeStore.t('strategy.sharpe')" :value="latestRun.metrics.sharpe_ratio.toFixed(2)" />
            <MetricTile :label="localeStore.t('strategy.maxDrawdown')" :value="formatPercent(latestRun.metrics.max_drawdown)" />
            <MetricTile :label="localeStore.t('strategy.winRate')" :value="formatPercent(latestRun.metrics.win_rate)" />
            <MetricTile :label="localeStore.t('strategy.tradeCount')" :value="String(latestRun.metrics.trade_count)" />
            <MetricTile :label="localeStore.t('strategy.excessReturn')" :value="latestRun.excess_return != null ? formatPercent(latestRun.excess_return) : '-'" />
          </div>
          <PerformanceChart :points="latestRun.equity_curve" />
          <SectionPanel :title="localeStore.t('strategy.monthlyHeatmap')">
            <MonthlyHeatmap :points="latestRun.monthly_returns" />
          </SectionPanel>
          <SectionPanel :title="localeStore.t('strategy.trades')">
            <TradeLogTable :rows="latestRun.trade_log" />
          </SectionPanel>
          <SectionPanel :title="localeStore.t('strategy.compare')">
            <CompareRunsTable :runs="runHistory" />
          </SectionPanel>
        </div>
        <div v-else class="panel empty-state">{{ localeStore.t('strategy.chooseToRun') }}</div>
      </SectionPanel>
    </div>
  </div>
</template>

<style scoped>
.strategy-layout,
.lab-grid,
.metrics-grid,
.results-grid {
  display: grid;
  gap: 20px;
}

.hero {
  padding: 30px;
}

.hero h2 {
  margin: 10px 0 12px;
  max-width: 700px;
  font-size: clamp(2rem, 3vw, 3rem);
  font-family: 'Chakra Petch', sans-serif;
}

.hero p {
  max-width: 720px;
  margin: 0;
  color: var(--text-secondary);
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
  grid-template-columns: 420px minmax(0, 1fr);
}

.metrics-grid {
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.empty-state {
  padding: 18px;
}

.error {
  color: var(--negative);
}

@media (max-width: 1200px) {
  .lab-grid,
  .metrics-grid {
    grid-template-columns: 1fr;
  }
}
</style>
