<script setup lang="ts">
import * as echarts from 'echarts'
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'

import type { EquityPoint } from '@/types'

const props = defineProps<{
  points: EquityPoint[]
}>()

const container = ref<HTMLDivElement | null>(null)
let chart: echarts.ECharts | null = null

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
    ],
  })
}

onMounted(renderChart)
watch(() => props.points, renderChart, { deep: true })

onBeforeUnmount(() => {
  chart?.dispose()
})
</script>

<template>
  <div ref="container" class="performance-chart" />
</template>

<style scoped>
.performance-chart {
  width: 100%;
  min-height: 320px;
}
</style>
