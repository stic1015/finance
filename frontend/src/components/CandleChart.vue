<script setup lang="ts">
import { createChart } from 'lightweight-charts'
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'

import type { CandleSeries } from '@/types'

const props = defineProps<{
  series: CandleSeries | null
}>()

const container = ref<HTMLDivElement | null>(null)
let chart: ReturnType<typeof createChart> | null = null

function renderChart() {
  if (!container.value || !props.series) return
  chart?.remove()
  chart = createChart(container.value, {
    height: 360,
    layout: {
      background: { color: '#0c1824' },
      textColor: '#98afc5',
    },
    grid: {
      vertLines: { color: 'rgba(255,255,255,0.04)' },
      horzLines: { color: 'rgba(255,255,255,0.04)' },
    },
    rightPriceScale: {
      borderColor: 'rgba(255,255,255,0.08)',
    },
    timeScale: {
      borderColor: 'rgba(255,255,255,0.08)',
    },
  })
  const candleSeries = chart.addCandlestickSeries({
    upColor: '#2fe08b',
    downColor: '#ff6b7a',
    borderVisible: false,
    wickUpColor: '#2fe08b',
    wickDownColor: '#ff6b7a',
  })
  candleSeries.setData(
    props.series.points.map((point) => ({
      time: point.timestamp.slice(0, 10),
      open: point.open,
      high: point.high,
      low: point.low,
      close: point.close,
    })),
  )
  chart.timeScale().fitContent()
}

onMounted(renderChart)
watch(() => props.series, renderChart, { deep: true })

onBeforeUnmount(() => {
  chart?.remove()
})
</script>

<template>
  <div ref="container" class="chart-frame" />
</template>

<style scoped>
.chart-frame {
  width: 100%;
  min-height: 360px;
  border-radius: 18px;
  overflow: hidden;
}
</style>
