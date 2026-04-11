<script setup lang="ts">
import { useLocaleStore } from '@/stores/locale'

const localeStore = useLocaleStore()

function handleChange(event: Event) {
  const target = event.target as HTMLSelectElement | null
  if (!target) return
  localeStore.setLocale(target.value as 'zh-CN' | 'en-US')
}
</script>

<template>
  <label class="locale-switcher panel">
    <span class="eyebrow">{{ localeStore.t('common.language') }}</span>
    <select :value="localeStore.locale" @change="handleChange">
      <option value="zh-CN">{{ localeStore.t('common.zhCN') }}</option>
      <option value="en-US">{{ localeStore.t('common.enUS') }}</option>
    </select>
  </label>
</template>

<style scoped>
.locale-switcher {
  display: grid;
  gap: 8px;
  padding: 10px 12px;
  min-width: 136px;
}

select {
  border: 1px solid var(--border);
  border-radius: 12px;
  background: rgba(4, 10, 16, 0.62);
  color: var(--text);
  padding: 8px 10px;
}
</style>
