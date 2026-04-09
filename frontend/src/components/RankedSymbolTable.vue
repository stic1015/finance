<script setup lang="ts">
import { useLocaleStore } from '@/stores/locale'
import type { MarketSnapshot } from '@/types'
import { compactNumber, formatCurrency, formatMarketPercent } from '@/utils/format'

defineProps<{
  items: MarketSnapshot[]
}>()

const localeStore = useLocaleStore()
</script>

<template>
  <div class="rank-table panel">
    <table>
      <thead>
        <tr>
          <th>#</th>
          <th>代码</th>
          <th>名称</th>
          <th>价格</th>
          <th>涨跌</th>
          <th>成交量</th>
          <th>状态</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(item, index) in items" :key="item.symbol">
          <td>{{ index + 1 }}</td>
          <td class="mono">{{ item.symbol }}</td>
          <td>{{ item.display_name }}</td>
          <td>{{ formatCurrency(item.price) }}</td>
          <td :class="item.change_percent >= 0 ? 'status-positive' : 'status-negative'">
            {{ formatMarketPercent(item.change_percent) }}
          </td>
          <td>{{ compactNumber(item.volume) }}</td>
          <td>{{ localeStore.t(`common.${item.source_status === 'live' ? 'realtime' : item.source_status === 'delayed' ? 'mixed' : item.source_status === 'fixture' ? 'simulated' : 'unavailable'}`) }}</td>
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
  padding: 10px 12px;
  border-bottom: 1px solid var(--border);
  text-align: left;
  white-space: nowrap;
}

th {
  font-size: 0.8rem;
  color: var(--text-muted);
  font-weight: 600;
}
</style>
