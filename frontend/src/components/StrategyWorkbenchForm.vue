<script setup lang="ts">
import { computed, reactive, watch } from 'vue'

import { FALLBACK_STRATEGIES, STRATEGY_FIELDS } from '@/constants/strategies'
import type { StrategyDefinition } from '@/types'

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

const props = defineProps<{
  strategies?: StrategyDefinition[]
}>()

const strategies = computed(() => (props.strategies?.length ? props.strategies : FALLBACK_STRATEGIES))

const form = reactive({
  symbol: 'HK.00700',
  strategy: 'trend_strength_volatility_filter',
  start_date: '2024-01-01T00:00:00Z',
  end_date: '2025-01-01T00:00:00Z',
  params: {} as Record<string, number>,
})

const activeStrategy = computed(() => strategies.value.find((item) => item.name === form.strategy) ?? strategies.value[0])
const activeFields = computed(() => STRATEGY_FIELDS[form.strategy] ?? [])

function syncDefaults() {
  const defaults = activeStrategy.value?.default_params ?? {}
  form.params = Object.fromEntries(Object.entries(defaults).map(([key, value]) => [key, Number(value)]))
}

watch(
  () => form.strategy,
  () => {
    syncDefaults()
  },
  { immediate: true },
)

function handleSubmit() {
  emit('submit', {
    symbol: form.symbol,
    strategy: form.strategy,
    start_date: form.start_date,
    end_date: form.end_date,
    params: form.params,
  })
}
</script>

<template>
  <form class="strategy-form panel" @submit.prevent="handleSubmit">
    <label>
      <span class="eyebrow">标的代码</span>
      <input v-model="form.symbol" />
    </label>
    <label>
      <span class="eyebrow">策略模板</span>
      <select v-model="form.strategy">
        <option v-for="strategy in strategies" :key="strategy.name" :value="strategy.name">
          {{ strategy.label }}
        </option>
      </select>
    </label>
    <div v-if="activeStrategy" class="strategy-hint panel">
      <div class="eyebrow">{{ activeStrategy.category }}</div>
      <strong>{{ activeStrategy.label }}</strong>
      <p>{{ activeStrategy.description }}</p>
    </div>
    <div class="grid grid-2">
      <label>
        <span class="eyebrow">开始时间</span>
        <input v-model="form.start_date" />
      </label>
      <label>
        <span class="eyebrow">结束时间</span>
        <input v-model="form.end_date" />
      </label>
    </div>
    <div class="grid grid-2">
      <label v-for="field in activeFields" :key="field.key">
        <span class="eyebrow">{{ field.label }}</span>
        <input v-model.number="form.params[field.key]" type="number" :min="field.min" :step="field.step ?? 1" />
      </label>
    </div>
    <button type="submit">运行回测</button>
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

.strategy-hint {
  padding: 16px;
}

.strategy-hint strong {
  display: block;
  margin: 8px 0;
  font-size: 1.15rem;
}

.strategy-hint p {
  margin: 0;
  color: var(--text-secondary);
  line-height: 1.5;
}
</style>
