<script setup lang="ts">
import { ref } from 'vue'

import { apiGet, apiPost } from '@/api/client'
import MetricTile from '@/components/MetricTile.vue'
import PerformanceChart from '@/components/PerformanceChart.vue'
import SectionPanel from '@/components/SectionPanel.vue'
import StrategyForm from '@/components/StrategyForm.vue'
import type { BacktestResult } from '@/types'
import { formatPercent } from '@/utils/format'

const backtest = ref<BacktestResult | null>(null)
const loading = ref(false)
const error = ref('')

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
    for (let attempt = 0; attempt < 6 && result.status === 'running'; attempt += 1) {
      await new Promise((resolve) => window.setTimeout(resolve, 1500))
      result = await apiGet<BacktestResult>(`/api/backtests/${queued.job_id}`)
    }
    backtest.value = result
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Failed to run backtest.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="strategy-layout">
    <section class="hero panel">
      <div>
        <div class="eyebrow">Template Strategies</div>
        <h2>Stress-test alpha ideas with benchmark-aware diagnostics.</h2>
        <p>
          Start with the built-in templates, adjust parameters, then compare cumulative return, drawdown, Sharpe, and
          equity curve behavior.
        </p>
      </div>
    </section>

    <div class="lab-grid">
      <SectionPanel title="Strategy Controls" subtitle="Input surface">
        <StrategyForm @submit="submitBacktest" />
      </SectionPanel>

      <SectionPanel title="Run Results" subtitle="Performance and caveats">
        <div v-if="loading" class="panel empty-state">Running backtest...</div>
        <div v-else-if="error" class="panel empty-state error">{{ error }}</div>
        <div v-else-if="backtest?.metrics" class="results-grid">
          <div class="metrics-grid">
            <MetricTile label="Cumulative Return" :value="formatPercent(backtest.metrics.cumulative_return)" />
            <MetricTile label="Annualized Return" :value="formatPercent(backtest.metrics.annualized_return)" />
            <MetricTile label="Sharpe Ratio" :value="backtest.metrics.sharpe_ratio.toFixed(2)" />
            <MetricTile label="Max Drawdown" :value="formatPercent(backtest.metrics.max_drawdown)" />
            <MetricTile label="Win Rate" :value="formatPercent(backtest.metrics.win_rate)" />
            <MetricTile label="Trades" :value="String(backtest.metrics.trade_count)" />
          </div>
          <PerformanceChart :points="backtest.equity_curve" />
          <div class="caveats panel">
            <div class="eyebrow">Research Notes</div>
            <ul>
              <li v-for="note in backtest.caveats" :key="note">{{ note }}</li>
            </ul>
          </div>
        </div>
        <div v-else class="panel empty-state">Choose a strategy and launch a run to populate this panel.</div>
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

.lab-grid {
  grid-template-columns: 420px minmax(0, 1fr);
}

.metrics-grid {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.caveats {
  padding: 18px;
}

.caveats ul {
  margin: 14px 0 0;
  padding-left: 18px;
  color: var(--text-secondary);
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
