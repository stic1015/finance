<script setup lang="ts">
import { useLocaleStore } from '@/stores/locale'
import type { BacktestResult } from '@/types'
import { formatPercent } from '@/utils/format'

defineProps<{
  runs: BacktestResult[]
}>()

const localeStore = useLocaleStore()
</script>

<template>
  <div class="compare-table panel">
    <table>
      <thead>
        <tr>
          <th>策略</th>
          <th>累计收益</th>
          <th>超额收益</th>
          <th>最大回撤</th>
          <th>Sharpe</th>
        </tr>
        <tr class="clean-head">
          <th>{{ localeStore.locale === 'zh-CN' ? '策略' : 'Strategy' }}</th>
          <th>{{ localeStore.t('strategy.cumulative') }}</th>
          <th>{{ localeStore.t('strategy.excessReturn') }}</th>
          <th>{{ localeStore.t('strategy.maxDrawdown') }}</th>
          <th>Sharpe</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="run in runs" :key="run.job_id">
          <td>{{ run.strategy }}</td>
          <td>{{ run.metrics ? formatPercent(run.metrics.cumulative_return) : '-' }}</td>
          <td>{{ run.excess_return != null ? formatPercent(run.excess_return) : '-' }}</td>
          <td>{{ run.metrics ? formatPercent(run.metrics.max_drawdown) : '-' }}</td>
          <td>{{ run.metrics ? run.metrics.sharpe_ratio.toFixed(2) : '-' }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
.compare-table {
  padding: 16px;
  overflow: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th,
td {
  padding: 12px;
  border-bottom: 1px solid var(--border-subtle);
  text-align: left;
}

th {
  color: var(--text-muted);
  font-size: 0.85rem;
  font-weight: 600;
}

thead tr:first-child {
  display: none;
}
</style>
