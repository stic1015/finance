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
  padding: 8px 12px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.06);
  color: var(--text-secondary);
  font-size: 0.85rem;
}

[data-tone='positive'] {
  background: rgba(47, 224, 139, 0.12);
  color: var(--positive);
}

[data-tone='negative'] {
  background: rgba(255, 107, 122, 0.12);
  color: var(--negative);
}
</style>
