<script setup lang="ts">
import type { NewsItem } from '@/types'
import { translateSentiment } from '@/utils/presentation'

defineProps<{
  item: NewsItem
}>()
</script>

<template>
  <a class="news-card panel" :href="item.url" target="_blank" rel="noreferrer">
    <div class="top-row">
      <span class="eyebrow">{{ item.source }}</span>
      <span class="sentiment" :data-tone="item.sentiment">{{ translateSentiment(item.sentiment) }}</span>
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
  box-shadow: var(--shadow);
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
  font-size: 1.02rem;
  line-height: 1.4;
}

p {
  color: var(--text-secondary);
  line-height: 1.55;
}

.sentiment {
  padding: 6px 10px;
  border-radius: 999px;
  border: 1px solid transparent;
  font-size: 0.72rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

[data-tone='positive'] {
  color: var(--positive);
  background: var(--positive-soft);
  border-color: rgba(57, 230, 146, 0.16);
}

[data-tone='negative'] {
  color: var(--negative);
  background: var(--negative-soft);
  border-color: rgba(255, 117, 134, 0.16);
}

[data-tone='neutral'] {
  color: var(--accent);
  background: var(--accent-soft);
  border-color: rgba(70, 212, 255, 0.16);
}

.foot-row {
  color: var(--text-muted);
  font-size: 0.72rem;
}
</style>
