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
    <div class="metric-copy">
      <div class="eyebrow">{{ label }}</div>
      <strong>{{ value }}</strong>
    </div>
    <span v-if="delta" :class="deltaClass">{{ delta }}</span>
  </article>
</template>

<style scoped>
.metric-tile {
  padding: 18px 18px 16px;
  min-height: 126px;
  display: grid;
  gap: 14px;
  align-content: space-between;
}

.metric-copy {
  display: grid;
  gap: 14px;
}

strong {
  font-size: clamp(1.7rem, 2vw, 2.3rem);
  line-height: 0.95;
  font-family: 'Chakra Petch', sans-serif;
  letter-spacing: -0.03em;
}

span {
  font-size: 0.85rem;
  font-weight: 600;
}

.metric-tile::before {
  content: '';
  position: absolute;
  left: 18px;
  right: 18px;
  bottom: 14px;
  height: 1px;
  background: linear-gradient(90deg, rgba(70, 212, 255, 0.36), transparent);
  pointer-events: none;
}
</style>
