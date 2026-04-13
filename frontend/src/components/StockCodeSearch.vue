<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'

import { useLocaleStore } from '@/stores/locale'

const router = useRouter()
const localeStore = useLocaleStore()
const query = ref('HK.00700')
const helperLabel = computed(() =>
  localeStore.locale === 'zh-CN'
    ? '支持港股 / A 股代码，输入后直接跳转研究页'
    : 'Jump straight into research with HK, SH, or SZ symbols.',
)

function normalizeInput(raw: string) {
  const value = raw.trim().toUpperCase().replace('/', '.')
  if (!value) return ''
  if (value.includes('.')) return value
  if (/^\d{5}$/.test(value)) return `HK.${value}`
  if (/^\d{6}$/.test(value)) {
    return value.startsWith('6') ? `SH.${value}` : `SZ.${value}`
  }
  return value
}

function goToSymbol() {
  const normalized = normalizeInput(query.value)
  if (!normalized) return
  void router.push(`/stocks/${normalized}`)
}
</script>

<template>
  <form class="search-bar glass-line" @submit.prevent="goToSymbol">
    <label class="search-field">
      <span class="eyebrow">{{ localeStore.locale === 'zh-CN' ? '研究跳转' : 'Research Jump' }}</span>
      <input v-model="query" :placeholder="localeStore.t('common.searchPlaceholder')" />
    </label>
    <button type="submit">{{ localeStore.t('common.search') }}</button>
    <p class="search-helper mono">{{ helperLabel }}</p>
  </form>
</template>

<style scoped>
.search-bar {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 10px 12px;
  padding: 14px;
}

.search-field {
  display: grid;
  gap: 10px;
}

input {
  width: 100%;
  min-height: 48px;
  border: 1px solid var(--border-subtle);
  border-radius: 16px;
  background: rgba(4, 10, 16, 0.72);
  color: var(--text);
  padding: 12px 14px;
}

input:focus {
  border-color: var(--border-strong);
  box-shadow: 0 0 0 1px rgba(70, 212, 255, 0.18);
}

button {
  min-width: 108px;
  border: none;
  border-radius: 16px;
  background: linear-gradient(135deg, var(--accent), var(--accent-2));
  color: #041019;
  font-weight: 700;
  padding: 0 18px;
  cursor: pointer;
}

.search-helper {
  grid-column: 1 / -1;
  margin: 0;
  color: var(--text-muted);
  font-size: 0.72rem;
}

@media (max-width: 720px) {
  .search-bar {
    grid-template-columns: 1fr;
  }

  button {
    min-height: 46px;
  }
}
</style>
