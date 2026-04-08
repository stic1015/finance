<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import { apiGet, apiPost } from '@/api/client'
import { FALLBACK_STRATEGIES } from '@/constants/strategies'
import MetricTile from '@/components/MetricTile.vue'
import PerformanceChart from '@/components/PerformanceChart.vue'
import SectionPanel from '@/components/SectionPanel.vue'
import StrategyWorkbenchForm from '@/components/StrategyWorkbenchForm.vue'
import type { BacktestResult, StrategyDefinition } from '@/types'
import { formatPercent } from '@/utils/format'

const backtest = ref<BacktestResult | null>(null)
const loading = ref(false)
const error = ref('')
const strategies = ref<StrategyDefinition[]>([])

const selectedStrategy = computed(
  () => strategies.value.find((item) => item.name === backtest.value?.strategy) ?? strategies.value[0] ?? FALLBACK_STRATEGIES[0],
)

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
    for (let attempt = 0; attempt < 6 && result.status === 'running'; attempt += 1) {
      await new Promise((resolve) => window.setTimeout(resolve, 1500))
      result = await apiGet<BacktestResult>(`/api/backtests/${queued.job_id}`)
    }
    backtest.value = result
  } catch (err) {
    error.value = err instanceof Error ? err.message : '运行回测失败。'
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
        <div class="eyebrow">机构化策略模板</div>
        <h2>把策略假设、风险约束和收益曲线放进同一个研究终端里验证。</h2>
        <p>先选模板，再调参数，最后对比累计收益、回撤、Sharpe 和权益曲线的稳定性。</p>
      </div>
    </section>

    <div class="lab-grid">
      <SectionPanel title="策略控制台" subtitle="模板与参数">
        <StrategyWorkbenchForm :strategies="strategies.length ? strategies : FALLBACK_STRATEGIES" @submit="submitBacktest" />
      </SectionPanel>

      <SectionPanel title="回测结果" subtitle="收益表现与研究备注">
        <div class="strategy-summary panel">
          <div class="eyebrow">{{ selectedStrategy.category }}</div>
          <strong>{{ selectedStrategy.label }}</strong>
          <p>{{ selectedStrategy.description }}</p>
          <p class="section-note">逻辑摘要：{{ selectedStrategy.logic_summary }}</p>
          <p class="section-note">风格标签：{{ selectedStrategy.style_tags.join(' / ') }}</p>
          <p class="section-note">适用市场：{{ selectedStrategy.market_scope.join(' / ') }}</p>
        </div>

        <div v-if="loading" class="panel empty-state">正在运行回测...</div>
        <div v-else-if="error" class="panel empty-state error">{{ error }}</div>
        <div v-else-if="backtest?.metrics" class="results-grid">
          <div class="metrics-grid">
            <MetricTile label="累计收益" :value="formatPercent(backtest.metrics.cumulative_return)" />
            <MetricTile label="年化收益" :value="formatPercent(backtest.metrics.annualized_return)" />
            <MetricTile label="Sharpe" :value="backtest.metrics.sharpe_ratio.toFixed(2)" />
            <MetricTile label="最大回撤" :value="formatPercent(backtest.metrics.max_drawdown)" />
            <MetricTile label="胜率" :value="formatPercent(backtest.metrics.win_rate)" />
            <MetricTile label="交易次数" :value="String(backtest.metrics.trade_count)" />
          </div>
          <PerformanceChart :points="backtest.equity_curve" />
          <div class="caveats panel">
            <div class="eyebrow">研究备注</div>
            <ul>
              <li v-for="note in backtest.caveats" :key="note">{{ note }}</li>
            </ul>
          </div>
        </div>
        <div v-else class="panel empty-state">选择一个策略模板并发起回测，这里会显示风险与收益结果。</div>
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
