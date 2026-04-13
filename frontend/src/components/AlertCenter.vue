<script setup lang="ts">
import { computed } from 'vue'

import { useLocaleStore } from '@/stores/locale'
import { useWatchStore } from '@/stores/watch'

const localeStore = useLocaleStore()
const watchStore = useWatchStore()

const unreadEvents = computed(() => watchStore.events.filter((event) => !event.read))
</script>

<template>
  <section class="alert-center panel">
    <header class="alert-head">
      <div class="alert-copy">
        <div class="eyebrow">{{ localeStore.t('alerts.center') }}</div>
        <h3>{{ unreadEvents.length }} {{ localeStore.t('alerts.unread') }}</h3>
      </div>
      <span class="alert-pill">{{ watchStore.events.length }}</span>
    </header>
    <div class="content">
      <article v-for="event in watchStore.events.slice(0, 6)" :key="event.id" class="event-row">
        <div>
          <strong>{{ event.symbol }}</strong>
          <p>{{ event.title }}</p>
        </div>
        <button type="button" @click="watchStore.markRead(event.id)">
          {{ event.read ? localeStore.t('alerts.read') : localeStore.t('alerts.unread') }}
        </button>
      </article>
      <div v-if="!watchStore.events.length" class="empty-state">
        {{ localeStore.t('alerts.noEvents') }}
      </div>
    </div>
  </section>
</template>

<style scoped>
.alert-center {
  padding: 18px;
}

.alert-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 16px;
}

.alert-copy {
  display: grid;
  gap: 8px;
}

h3,
p,
strong {
  margin: 0;
}

.alert-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 36px;
  min-height: 36px;
  padding: 0 10px;
  border-radius: 999px;
  border: 1px solid var(--border);
  color: var(--accent);
  background: var(--accent-soft);
  font-family: 'Chakra Petch', sans-serif;
}

.content {
  display: grid;
  gap: 12px;
}

.event-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  padding: 14px 14px 14px 16px;
  border-radius: 18px;
  border: 1px solid var(--border-subtle);
  background: rgba(255, 255, 255, 0.025);
}

.event-row p,
.empty-state {
  color: var(--text-secondary);
}

.event-row strong {
  display: block;
  margin-bottom: 6px;
  font-family: 'Chakra Petch', sans-serif;
}

button {
  border: 1px solid var(--border-subtle);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.02);
  color: var(--text);
  padding: 10px 12px;
  cursor: pointer;
}
</style>
