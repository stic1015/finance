<script setup lang="ts">
import type { SourceStatus } from '@/types'

defineProps<{
  label: string
  status: SourceStatus
}>()
</script>

<template>
  <div class="provider-badge" :data-status="status">
    <span class="dot" />
    <span>{{ label }}</span>
  </div>
</template>

<style scoped>
.provider-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  border-radius: 999px;
  border: 1px solid var(--border);
  color: var(--text-secondary);
  background: rgba(255, 255, 255, 0.03);
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 999px;
  background: var(--accent);
  box-shadow: 0 0 16px var(--accent-glow);
}

[data-status='live'] .dot {
  background: var(--positive);
}

[data-status='unavailable'] .dot {
  background: var(--negative);
}

[data-status='fixture'] .dot {
  background: var(--warning);
}

[data-status='delayed'] .dot {
  background: #6bd0ff;
}
</style>
