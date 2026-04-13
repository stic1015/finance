<script setup lang="ts">
defineProps<{
  title: string
  subtitle?: string
}>()
</script>

<template>
  <section class="section-panel panel">
    <header class="section-head">
      <div class="section-copy">
        <div class="eyebrow">{{ subtitle ?? '研究模块' }}</div>
        <h2>{{ title }}</h2>
      </div>
      <div v-if="$slots.actions" class="section-actions">
        <slot name="actions" />
      </div>
    </header>
    <div class="content">
      <slot />
    </div>
  </section>
</template>

<style scoped>
.section-panel {
  padding: 22px 22px 20px;
}

.section-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 18px;
  padding-bottom: 14px;
  border-bottom: 1px solid var(--border-subtle);
}

.section-copy {
  display: grid;
  gap: 8px;
}

.section-actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 10px;
}

h2 {
  margin: 0;
  font-size: clamp(1.08rem, 1.25vw, 1.34rem);
  font-weight: 600;
  letter-spacing: -0.02em;
}

.content {
  display: grid;
  gap: 16px;
}

@media (max-width: 720px) {
  .section-head {
    flex-direction: column;
  }

  .section-actions {
    justify-content: flex-start;
  }
}
</style>
