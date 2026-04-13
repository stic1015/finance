<script setup lang="ts">
import { useLocaleStore } from '@/stores/locale'
import type { TradeLogEntry } from '@/types'
import { translateTradeAction } from '@/utils/presentation'

withDefaults(
  defineProps<{
    rows: TradeLogEntry[]
    emptyLabel?: string
  }>(),
  {
    emptyLabel: '',
  },
)

const localeStore = useLocaleStore()
</script>

<template>
  <div class="trade-table panel">
    <table>
      <thead>
        <tr>
          <th>{{ localeStore.t('common.time') }}</th>
          <th>{{ localeStore.t('common.action') }}</th>
          <th>{{ localeStore.t('common.price') }}</th>
          <th>{{ localeStore.t('strategy.previousExposure') }}</th>
          <th>{{ localeStore.t('common.exposure') }}</th>
          <th>{{ localeStore.t('strategy.endEquity') }}</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="row in rows" :key="`${row.timestamp}-${row.action}-${row.price}`">
          <td>{{ new Date(row.timestamp).toLocaleString() }}</td>
          <td>{{ translateTradeAction(row.action, localeStore.locale) }}</td>
          <td>{{ row.price.toFixed(2) }}</td>
          <td>{{ row.previous_exposure.toFixed(2) }}</td>
          <td>{{ row.exposure.toFixed(2) }}</td>
          <td>{{ row.equity != null ? row.equity.toFixed(2) : '-' }}</td>
        </tr>
      </tbody>
    </table>
    <div v-if="!rows.length" class="empty-state">
      {{ emptyLabel || localeStore.t('strategy.noTradesForMonth') }}
    </div>
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
  padding: 12px;
  border-bottom: 1px solid var(--border-subtle);
  text-align: left;
  white-space: nowrap;
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
