<script setup lang="ts">
import type { NewsItem } from '@/types'

defineProps<{
  item: NewsItem
}>()
</script>

<template>
  <a class="news-card panel" :href="item.url" target="_blank" rel="noreferrer">
    <div class="top-row">
      <span class="eyebrow">{{ item.source }}</span>
      <span class="sentiment" :data-tone="item.sentiment">{{ item.sentiment }}</span>
    </div>
    <h3>{{ item.title }}</h3>
    <p>{{ item.summary }}</p>
    <div class="foot-row">
      <span class="mono">{{ new Date(item.published_at).toLocaleString() }}</span>
      <span class="mono">{{ item.matched_symbols.join(', ') }}</span>
    </div>
  </a>
</template>

<style scoped>
.news-card {
  display: grid;
  gap: 12px;
  padding: 18px;
  transition: transform 160ms ease, border-color 160ms ease;
}

.news-card:hover {
  transform: translateY(-2px);
  border-color: var(--border-strong);
}

.top-row,
.foot-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

h3,
p {
  margin: 0;
}

h3 {
  font-size: 1rem;
}

p {
  color: var(--text-secondary);
  line-height: 1.55;
}

.sentiment {
  padding: 6px 10px;
  border-radius: 999px;
  font-size: 0.75rem;
  text-transform: capitalize;
}

[data-tone='positive'] {
  color: var(--positive);
  background: rgba(47, 224, 139, 0.1);
}

[data-tone='negative'] {
  color: var(--negative);
  background: rgba(255, 107, 122, 0.1);
}

[data-tone='neutral'] {
  color: var(--accent);
  background: rgba(55, 214, 255, 0.1);
}

.foot-row {
  color: var(--text-muted);
  font-size: 0.72rem;
}
</style>
