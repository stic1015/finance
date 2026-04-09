<script setup lang="ts">
import { useLocaleStore } from '@/stores/locale'
import type { TradeLogEntry } from '@/types'

defineProps<{
  rows: TradeLogEntry[]
}>()

const localeStore = useLocaleStore()

function actionLabel(action: TradeLogEntry['action']) {
  if (action === 'buy') return '买入'
  if (action === 'sell') return '卖出'
  return '调仓'
}
</script>

<template>
  <div class="trade-table panel">
    <table>
      <thead>
        <tr>
          <th>时间</th>
          <th>动作</th>
          <th>价格</th>
          <th>仓位</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="row in rows.slice(0, 20)" :key="`${row.timestamp}-${row.action}`">
          <td>{{ new Date(row.timestamp).toLocaleString() }}</td>
          <td>{{ actionLabel(row.action) }}</td>
          <td>{{ row.price.toFixed(2) }}</td>
          <td>{{ row.exposure.toFixed(2) }}</td>
        </tr>
      </tbody>
    </table>
    <div v-if="!rows.length" class="empty-state">{{ localeStore.t('common.loading') }}</div>
  </div>
</template>

<style scoped>
.trade-table {
  padding: 16px;
  overflow: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th,
td {
  padding: 10px 12px;
  border-bottom: 1px solid var(--border);
  text-align: left;
}

th {
  color: var(--text-muted);
  font-size: 0.85rem;
  font-weight: 600;
}

.empty-state {
  color: var(--text-secondary);
  padding: 8px 4px 0;
}
</style>
