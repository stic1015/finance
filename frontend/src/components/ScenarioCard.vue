<script setup lang="ts">
import type { ForecastScenario } from '@/types'

defineProps<{
  scenario: ForecastScenario
}>()
</script>

<template>
  <article class="scenario-card panel" :data-label="scenario.label">
    <div class="eyebrow">{{ scenario.label }} Scenario</div>
    <strong>{{ (scenario.probability * 100).toFixed(1) }}%</strong>
    <p>{{ (scenario.expected_return * 100).toFixed(2) }}% expected return</p>
  </article>
</template>

<style scoped>
.scenario-card {
  padding: 18px;
  min-height: 132px;
}

strong {
  display: block;
  margin: 12px 0 8px;
  font-size: 1.75rem;
  font-family: 'Chakra Petch', sans-serif;
}

p {
  margin: 0;
  color: var(--text-secondary);
}

[data-label='bullish'] {
  box-shadow: inset 0 0 0 1px rgba(47, 224, 139, 0.16);
}

[data-label='bearish'] {
  box-shadow: inset 0 0 0 1px rgba(255, 107, 122, 0.16);
}
</style>
