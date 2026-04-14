<script setup lang="ts">
import { computed, reactive, watch } from 'vue'

import { FALLBACK_STRATEGIES, getStrategyFields, localizeStrategies } from '@/constants/strategies'
import { useLocaleStore } from '@/stores/locale'
import type { StrategyDefinition } from '@/types'

const emit = defineEmits<{
  submit: [
    payload: {
      symbol: string
      strategy: string
      interval: string
      start_date: string
      end_date: string
      params: Record<string, number>
    },
  ]
}>()

const props = defineProps<{
  strategies?: StrategyDefinition[]
}>()

const localeStore = useLocaleStore()
const strategies = computed(() =>
  localizeStrategies(props.strategies?.length ? props.strategies : FALLBACK_STRATEGIES, localeStore.locale),
)

const form = reactive({
  symbol: 'HK.00700',
  strategy: 'trend_strength_volatility_filter',
  interval: '30m',
  start_date: '2024-01-01T00:00:00Z',
  end_date: '2025-01-01T00:00:00Z',
  params: {} as Record<string, number>,
})

const activeStrategy = computed(() => strategies.value.find((item) => item.name === form.strategy) ?? strategies.value[0])
const activeFields = computed(() => getStrategyFields(form.strategy, localeStore.locale))

function syncDefaults() {
  const defaults = activeStrategy.value?.default_params ?? {}
  form.params = Object.fromEntries(Object.entries(defaults).map(([key, value]) => [key, Number(value)]))
}

watch(
  () => form.strategy,
  () => syncDefaults(),
  { immediate: true },
)

function handleSubmit() {
  emit('submit', {
    symbol: form.symbol,
    strategy: form.strategy,
    interval: form.interval,
    start_date: form.start_date,
    end_date: form.end_date,
    params: form.params,
  })
}
</script>

<template>
  <form class="strategy-form" @submit.prevent="handleSubmit">
    <label>
      <span class="eyebrow">{{ localeStore.t('strategy.symbol') }}</span>
      <input v-model="form.symbol" />
    </label>
    <label>
      <span class="eyebrow">{{ localeStore.t('strategy.strategyTemplate') }}</span>
      <select v-model="form.strategy">
        <option v-for="strategy in strategies" :key="strategy.name" :value="strategy.name">
          {{ strategy.label }}
        </option>
      </select>
    </label>
    <label>
      <span class="eyebrow">{{ localeStore.locale === 'zh-CN' ? '回测周期' : 'Backtest Interval' }}</span>
      <select v-model="form.interval">
        <option value="1d">1d</option>
        <option value="1h">1h</option>
        <option value="30m">30m</option>
        <option value="15m">15m</option>
      </select>
    </label>
    <div v-if="activeStrategy" class="strategy-hint glass-line">
      <div class="eyebrow">{{ activeStrategy.category }}</div>
      <strong>{{ activeStrategy.label }}</strong>
      <p>{{ activeStrategy.description }}</p>
    </div>
    <div class="grid grid-2">
      <label>
        <span class="eyebrow">{{ localeStore.t('strategy.startDate') }}</span>
        <input v-model="form.start_date" />
      </label>
      <label>
        <span class="eyebrow">{{ localeStore.t('strategy.endDate') }}</span>
        <input v-model="form.end_date" />
      </label>
    </div>
    <div class="grid grid-2">
      <label v-for="field in activeFields" :key="field.key">
        <span class="eyebrow">{{ field.label }}</span>
        <input v-model.number="form.params[field.key]" type="number" :min="field.min" :step="field.step ?? 1" />
      </label>
    </div>
    <button type="submit">{{ localeStore.t('strategy.runBacktest') }}</button>
  </form>
</template>

<style scoped>
.strategy-form {
  display: grid;
  gap: 16px;
}

label {
  display: grid;
  gap: 8px;
}

input,
select {
  width: 100%;
  min-height: 48px;
  padding: 14px 16px;
  border-radius: 16px;
  border: 1px solid var(--border-subtle);
  color: var(--text);
  background: rgba(4, 10, 16, 0.72);
}

input:focus,
select:focus {
  border-color: var(--border-strong);
}

button {
  min-height: 50px;
  padding: 15px 18px;
  border: none;
  border-radius: 16px;
  background: linear-gradient(135deg, var(--accent), var(--accent-2));
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
