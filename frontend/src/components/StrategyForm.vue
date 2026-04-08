<script setup lang="ts">
import { reactive } from 'vue'

const emit = defineEmits<{
  submit: [
    payload: {
      symbol: string
      strategy: string
      start_date: string
      end_date: string
      params: Record<string, number>
    },
  ]
}>()

const form = reactive({
  symbol: 'US.AAPL',
  strategy: 'moving_average_trend',
  start_date: '2024-01-01T00:00:00Z',
  end_date: '2025-01-01T00:00:00Z',
  fast_window: 20,
  slow_window: 60,
})

function handleSubmit() {
  emit('submit', {
    symbol: form.symbol,
    strategy: form.strategy,
    start_date: form.start_date,
    end_date: form.end_date,
    params: {
      fast_window: form.fast_window,
      slow_window: form.slow_window,
    },
  })
}
</script>

<template>
  <form class="strategy-form panel" @submit.prevent="handleSubmit">
    <label>
      <span class="eyebrow">Symbol</span>
      <input v-model="form.symbol" />
    </label>
    <label>
      <span class="eyebrow">Strategy</span>
      <select v-model="form.strategy">
        <option value="moving_average_trend">Moving Average Trend</option>
        <option value="rsi_bollinger_mean_reversion">RSI + Bollinger Mean Reversion</option>
        <option value="donchian_volume_breakout">Donchian + Volume Breakout</option>
        <option value="macd_trend_confirmation">MACD Trend Confirmation</option>
      </select>
    </label>
    <div class="grid grid-2">
      <label>
        <span class="eyebrow">Start</span>
        <input v-model="form.start_date" />
      </label>
      <label>
        <span class="eyebrow">End</span>
        <input v-model="form.end_date" />
      </label>
    </div>
    <div class="grid grid-2">
      <label>
        <span class="eyebrow">Fast Window</span>
        <input v-model.number="form.fast_window" type="number" min="2" />
      </label>
      <label>
        <span class="eyebrow">Slow Window</span>
        <input v-model.number="form.slow_window" type="number" min="5" />
      </label>
    </div>
    <button type="submit">Run Backtest</button>
  </form>
</template>

<style scoped>
.strategy-form {
  display: grid;
  gap: 16px;
  padding: 20px;
}

label {
  display: grid;
  gap: 8px;
}

input,
select {
  width: 100%;
  padding: 14px 16px;
  border-radius: 14px;
  border: 1px solid var(--border);
  color: var(--text);
  background: rgba(4, 10, 16, 0.62);
}

button {
  padding: 15px 18px;
  border: none;
  border-radius: 14px;
  background: linear-gradient(90deg, var(--accent), var(--accent-2));
  color: #021018;
  font-weight: 700;
  cursor: pointer;
}

.grid-2 {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}
</style>
