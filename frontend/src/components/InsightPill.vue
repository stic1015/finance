<script setup lang="ts">
defineProps<{
  label: string
  tone?: 'neutral' | 'positive' | 'negative'
}>()
</script>

<template>
  <span class="insight-pill" :data-tone="tone ?? 'neutral'">{{ label }}</span>
</template>

<style scoped>
.insight-pill {
  display: inline-flex;
  align-items: center;
  min-height: 38px;
  padding: 8px 13px;
  border-radius: 999px;
  border: 1px solid var(--border-subtle);
  background: rgba(255, 255, 255, 0.04);
  color: var(--text-secondary);
  font-size: 0.82rem;
}

[data-tone='positive'] {
  background: var(--positive-soft);
  border-color: rgba(57, 230, 146, 0.2);
  color: var(--positive);
}

[data-tone='negative'] {
  background: var(--negative-soft);
  border-color: rgba(255, 117, 134, 0.2);
  color: var(--negative);
}
</style>
