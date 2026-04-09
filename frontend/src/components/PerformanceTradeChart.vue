<script setup lang="ts">
import * as echarts from 'echarts'
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'

import type { EquityPoint, TradeLogEntry } from '@/types'

const props = defineProps<{
  points: EquityPoint[]
  trades: TradeLogEntry[]
}>()

const container = ref<HTMLDivElement | null>(null)
let chart: echarts.ECharts | null = null

function buildTradeMarkers() {
  const indexByDate = new Map(props.points.map((point, index) => [point.timestamp.slice(0, 10), index]))
  return props.trades
    .map((trade) => {
      const dateKey = trade.timestamp.slice(0, 10)
      const index = indexByDate.get(dateKey)
      if (index == null) return null
      return {
        coord: [index, trade.price],
        value: trade.action,
        itemStyle: {
          color: trade.action === 'buy' ? '#2fe08b' : trade.action === 'sell' ? '#ff6b7a' : '#ffbf5a',
        },
      }
    })
    .filter(Boolean)
}

function renderChart() {
  if (!container.value || !props.points.length) return
  chart ??= echarts.init(container.value)
  chart.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis' },
    grid: { left: 20, right: 20, top: 20, bottom: 20, containLabel: true },
    textStyle: { color: '#98afc5', fontFamily: 'IBM Plex Sans' },
    xAxis: {
      type: 'category',
      data: props.points.map((point) => point.timestamp.slice(0, 10)),
      axisLine: { lineStyle: { color: 'rgba(255,255,255,0.12)' } },
    },
    yAxis: {
      type: 'value',
      splitLine: { lineStyle: { color: 'rgba(255,255,255,0.06)' } },
    },
    series: [
      {
        name: 'Strategy',
        type: 'line',
        smooth: true,
        data: props.points.map((point) => point.equity),
        lineStyle: { color: '#37d6ff', width: 3 },
        areaStyle: { color: 'rgba(55, 214, 255, 0.12)' },
      },
      {
        name: 'Benchmark',
        type: 'line',
        smooth: true,
        data: props.points.map((point) => point.benchmark_equity),
        lineStyle: { color: '#ffbf5a', width: 2, type: 'dashed' },
      },
      {
        name: 'Trades',
        type: 'scatter',
        data: buildTradeMarkers().map((marker) => ({
          value: marker!.coord,
          itemStyle: marker!.itemStyle,
        })),
        symbolSize: 12,
      },
    ],
  })
}

onMounted(renderChart)
watch(() => [props.points, props.trades], renderChart, { deep: true })
onBeforeUnmount(() => chart?.dispose())
</script>

<template>
  <div ref="container" class="performance-chart" />
</template>

<style scoped>
.performance-chart {
  width: 100%;
  min-height: 360px;
}
</style>
