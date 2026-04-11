<script setup lang="ts">
import * as echarts from 'echarts'
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'

import { useLocaleStore } from '@/stores/locale'
import type { EquityPoint, TradeLogEntry } from '@/types'
import { translateTradeAction } from '@/utils/presentation'

const props = withDefaults(
  defineProps<{
    points: EquityPoint[]
    trades: TradeLogEntry[]
    selectedMonth?: string | null
  }>(),
  {
    selectedMonth: null,
  },
)

const localeStore = useLocaleStore()
const container = ref<HTMLDivElement | null>(null)
let chart: echarts.ECharts | null = null

function buildTradeMarkers() {
  const indexByDate = new Map(props.points.map((point, index) => [point.timestamp.slice(0, 10), index]))
  return props.trades
    .filter((trade) => !props.selectedMonth || trade.month === props.selectedMonth)
    .map((trade) => {
      const dateKey = trade.timestamp.slice(0, 10)
      const index = indexByDate.get(dateKey)
      if (index == null) return null
      return {
        coord: [index, trade.price],
        itemStyle: {
          color: trade.action === 'buy' ? '#2fe08b' : trade.action === 'sell' ? '#ff6b7a' : '#ffbf5a',
        },
        meta: trade,
      }
    })
    .filter(Boolean)
}

function renderChart() {
  if (!container.value || !props.points.length) return
  chart ??= echarts.init(container.value)

  const strategyLabel = localeStore.locale === 'zh-CN' ? '策略权益' : 'Strategy Equity'
  const benchmarkLabel = localeStore.locale === 'zh-CN' ? '基准权益' : 'Benchmark Equity'
  const tradeLabel = localeStore.t('strategy.tradeMarkers')
  const markers = buildTradeMarkers()

  chart.setOption({
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      formatter: (params: any[]) => {
        const lines = [`${params[0]?.axisValueLabel ?? ''}`]
        for (const param of params) {
          if (param.seriesName === tradeLabel && param.data?.meta) {
            const trade = param.data.meta as TradeLogEntry
            lines.push(
              `${translateTradeAction(trade.action, localeStore.locale)} | ${localeStore.t('common.price')} ${trade.price.toFixed(2)}`,
            )
            lines.push(
              `${localeStore.t('strategy.previousExposure')} ${trade.previous_exposure.toFixed(2)} -> ${localeStore.t('common.exposure')} ${trade.exposure.toFixed(2)}`,
            )
            if (trade.equity != null) {
              lines.push(`${localeStore.t('strategy.endEquity')} ${trade.equity.toFixed(2)}`)
            }
          } else {
            lines.push(`${param.seriesName}: ${Number(param.data).toFixed(2)}`)
          }
        }
        return lines.join('<br/>')
      },
    },
    legend: {
      top: 0,
      textStyle: { color: '#98afc5' },
      data: [strategyLabel, benchmarkLabel, tradeLabel],
    },
    grid: { left: 20, right: 20, top: 40, bottom: 20, containLabel: true },
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
        name: strategyLabel,
        type: 'line',
        smooth: true,
        data: props.points.map((point) => point.equity),
        lineStyle: { color: '#37d6ff', width: 3 },
        areaStyle: { color: 'rgba(55, 214, 255, 0.12)' },
      },
      {
        name: benchmarkLabel,
        type: 'line',
        smooth: true,
        data: props.points.map((point) => point.benchmark_equity),
        lineStyle: { color: '#ffbf5a', width: 2, type: 'dashed' },
      },
      {
        name: tradeLabel,
        type: 'scatter',
        data: markers.map((marker) => ({
          value: marker!.coord,
          itemStyle: marker!.itemStyle,
          meta: marker!.meta,
        })),
        symbolSize: 12,
      },
    ],
  })
}

onMounted(renderChart)
watch(
  () => [props.points, props.trades, props.selectedMonth, localeStore.locale],
  renderChart,
  { deep: true },
)
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
