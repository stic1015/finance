<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const query = ref('HK.00700')

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
  <form class="search-bar panel" @submit.prevent="goToSymbol">
    <input v-model="query" placeholder="输入港股/A股代码，例如 HK.00700 / 600519" />
    <button type="submit">搜索</button>
  </form>
</template>

<style scoped>
.search-bar {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 10px;
  padding: 12px;
}

input {
  border: 1px solid var(--border);
  border-radius: 12px;
  background: rgba(4, 10, 16, 0.62);
  color: var(--text);
  padding: 12px 14px;
}

button {
  border: none;
  border-radius: 12px;
  background: linear-gradient(90deg, var(--accent), var(--accent-2));
  color: #041019;
  font-weight: 700;
  padding: 12px 16px;
  cursor: pointer;
}
</style>
