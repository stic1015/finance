<script setup lang="ts">
defineProps<{
  title: string
  subtitle?: string
}>()
</script>

<template>
  <section class="section-panel panel">
    <header>
      <div>
        <div class="eyebrow">{{ subtitle ?? 'Research Module' }}</div>
        <h2>{{ title }}</h2>
      </div>
      <slot name="actions" />
    </header>
    <div class="content">
      <slot />
    </div>
  </section>
</template>

<style scoped>
.section-panel {
  padding: 22px;
}

header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 18px;
}

h2 {
  margin: 8px 0 0;
  font-size: 1.25rem;
}

.content {
  display: grid;
  gap: 16px;
}
</style>
