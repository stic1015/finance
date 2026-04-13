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
  min-height: 34px;
  padding: 7px 12px;
  border-radius: 999px;
  border: 1px solid var(--border-subtle);
  color: var(--text-secondary);
  background: rgba(255, 255, 255, 0.025);
  font-size: 0.78rem;
  letter-spacing: 0.01em;
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
  box-shadow: 0 0 16px rgba(57, 230, 146, 0.24);
}

[data-status='unavailable'] .dot {
  background: var(--negative);
  box-shadow: 0 0 16px rgba(255, 117, 134, 0.24);
}

[data-status='fixture'] .dot {
  background: var(--warning);
  box-shadow: 0 0 16px rgba(255, 200, 106, 0.24);
}

[data-status='delayed'] .dot {
  background: #6bd0ff;
}

[data-status='live'] {
  border-color: rgba(57, 230, 146, 0.22);
}

[data-status='unavailable'] {
  border-color: rgba(255, 117, 134, 0.22);
}
</style>
