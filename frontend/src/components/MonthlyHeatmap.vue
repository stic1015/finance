<script setup lang="ts">
import * as echarts from 'echarts'
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'

import type { MonthlyReturnPoint } from '@/types'

const props = defineProps<{
  points: MonthlyReturnPoint[]
}>()

const container = ref<HTMLDivElement | null>(null)
let chart: echarts.ECharts | null = null

function renderChart() {
  if (!container.value || !props.points.length) return
  chart ??= echarts.init(container.value)
  chart.setOption({
    backgroundColor: 'transparent',
    grid: { left: 10, right: 10, top: 20, bottom: 10, containLabel: true },
    xAxis: {
      type: 'category',
      data: props.points.map((point) => point.month),
      axisLabel: { color: '#98afc5', rotate: 30 },
      axisLine: { lineStyle: { color: 'rgba(255,255,255,0.12)' } },
    },
    yAxis: { type: 'category', data: ['return'], axisLabel: { color: '#98afc5' } },
    visualMap: {
      min: -0.1,
      max: 0.1,
      orient: 'horizontal',
      show: false,
      inRange: { color: ['#ff6b7a', '#1b2635', '#2fe08b'] },
    },
    series: [
      {
        type: 'heatmap',
        data: props.points.map((point, index) => [index, 0, point.return_rate]),
        label: {
          show: true,
          formatter: ({ data }: { data: [number, number, number] }) => `${(data[2] * 100).toFixed(1)}%`,
          color: '#eff7ff',
        },
      },
    ],
  })
}

onMounted(renderChart)
watch(() => props.points, renderChart, { deep: true })
onBeforeUnmount(() => chart?.dispose())
</script>

<template>
  <div ref="container" class="heatmap" />
</template>

<style scoped>
.heatmap {
  width: 100%;
  min-height: 220px;
}
</style>
