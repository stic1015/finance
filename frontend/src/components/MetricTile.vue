<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  label: string
  value: string
  delta?: string
  positive?: boolean | null
}>()

const deltaClass = computed(() => {
  if (props.positive === true) return 'status-positive'
  if (props.positive === false) return 'status-negative'
  return 'status-neutral'
})
</script>

<template>
  <article class="metric-tile panel">
    <div class="eyebrow">{{ label }}</div>
    <strong>{{ value }}</strong>
    <span v-if="delta" :class="deltaClass">{{ delta }}</span>
  </article>
</template>

<style scoped>
.metric-tile {
  padding: 18px;
  min-height: 122px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

strong {
  font-size: 1.9rem;
  line-height: 1;
  font-family: 'Chakra Petch', sans-serif;
}

span {
  font-size: 0.95rem;
}
</style>
