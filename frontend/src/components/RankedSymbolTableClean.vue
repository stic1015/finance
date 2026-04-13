<script setup lang="ts">
import { useLocaleStore } from '@/stores/locale'
import type { MarketSnapshot } from '@/types'
import { compactNumber, formatCurrency, formatMarketPercent } from '@/utils/format'

defineProps<{
  items: MarketSnapshot[]
}>()

const localeStore = useLocaleStore()

function statusLabel(status: MarketSnapshot['source_status']) {
  if (status === 'live') return localeStore.t('common.realtime')
  if (status === 'delayed') return localeStore.t('common.mixed')
  if (status === 'fixture') return localeStore.t('common.simulated')
  return localeStore.t('common.unavailable')
}
</script>

<template>
  <div class="rank-table panel">
    <table>
      <thead>
        <tr>
          <th>#</th>
          <th>{{ localeStore.t('common.code') }}</th>
          <th>{{ localeStore.t('common.name') }}</th>
          <th>{{ localeStore.t('common.price') }}</th>
          <th>{{ localeStore.t('overview.movers') }}</th>
          <th>{{ localeStore.t('common.volume') }}</th>
          <th>{{ localeStore.t('common.status') }}</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(item, index) in items" :key="item.symbol">
          <td>{{ index + 1 }}</td>
          <td class="mono">
            <RouterLink class="symbol-link" :to="`/stocks/${item.symbol}`">{{ item.symbol }}</RouterLink>
          </td>
          <td>
            <RouterLink class="name-link" :to="`/stocks/${item.symbol}`">{{ item.display_name }}</RouterLink>
          </td>
          <td>{{ formatCurrency(item.price) }}</td>
          <td :class="item.change_percent >= 0 ? 'status-positive' : 'status-negative'">
            {{ formatMarketPercent(item.change_percent) }}
          </td>
          <td>{{ compactNumber(item.volume) }}</td>
          <td>{{ statusLabel(item.source_status) }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
.rank-table {
  padding: 10px 12px;
  overflow: auto;
  max-height: 760px;
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
  font-size: 0.8rem;
  color: var(--text-muted);
  font-weight: 600;
}

tbody tr {
  transition: background 160ms ease;
}

tbody tr:hover {
  background: rgba(255, 255, 255, 0.025);
}

.symbol-link,
.name-link {
  display: inline-flex;
  align-items: center;
  min-height: 24px;
}

.symbol-link {
  color: var(--accent);
}

.name-link {
  font-weight: 500;
}
</style>
