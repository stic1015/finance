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
  <label class="locale-switcher glass-line">
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
  gap: 10px;
  padding: 12px 14px;
  min-width: 152px;
}

select {
  min-height: 42px;
  border: 1px solid var(--border-subtle);
  border-radius: 14px;
  background: rgba(4, 10, 16, 0.72);
  color: var(--text);
  padding: 8px 12px;
}

select:focus {
  border-color: var(--border-strong);
}
</style>
