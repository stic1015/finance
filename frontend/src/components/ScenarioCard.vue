<script setup lang="ts">
import { computed } from 'vue'

import { useLocaleStore } from '@/stores/locale'
import type { ForecastScenario } from '@/types'
import { translateScenario } from '@/utils/presentation'

const props = defineProps<{
  scenario: ForecastScenario
}>()

const localeStore = useLocaleStore()
const scenario = computed(() => props.scenario)
const scenarioHeading = computed(() => `${translateScenario(props.scenario.label)} Scenario`)
const expectedHeading = computed(() => `Expected Return ${(props.scenario.expected_return * 100).toFixed(2)}%`)
const scenarioTitle = computed(
  () => `${translateScenario(props.scenario.label)} ${localeStore.locale === 'zh-CN' ? '场景' : 'Scenario'}`,
)
const expectedLabel = computed(
  () => `${localeStore.locale === 'zh-CN' ? '预期收益' : 'Expected Return'} ${(props.scenario.expected_return * 100).toFixed(2)}%`,
)
</script>

<template>
  <article
    class="scenario-card panel"
    :data-label="props.scenario.label"
    :data-title="scenarioHeading"
    :data-expected="expectedHeading"
  >
    <div class="eyebrow">{{ translateScenario(scenario.label) }}场景</div>
    <strong>{{ (props.scenario.probability * 100).toFixed(1) }}%</strong>
    <p>预期收益 {{ (scenario.expected_return * 100).toFixed(2) }}%</p>
  </article>
</template>

<style scoped>
.scenario-card {
  display: grid;
  gap: 8px;
  padding: 18px;
  min-height: 132px;
}

.scenario-card::before {
  content: attr(data-title);
  display: block;
  font-size: 11px;
  line-height: 1;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--text-muted);
}

strong {
  display: block;
  margin: 4px 0;
  font-size: 1.75rem;
  font-family: 'Chakra Petch', sans-serif;
}

.scenario-card::after {
  content: attr(data-expected);
  display: block;
  font-size: 1rem;
  line-height: 1.55;
  color: var(--text-secondary);
}

.eyebrow,
p {
  display: none;
}

[data-label='bullish'] {
  box-shadow: inset 0 0 0 1px rgba(47, 224, 139, 0.16);
}

[data-label='bearish'] {
  box-shadow: inset 0 0 0 1px rgba(255, 107, 122, 0.16);
}
</style>
