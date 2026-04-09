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
    <header>
      <div>
        <div class="eyebrow">{{ localeStore.t('alerts.center') }}</div>
        <h3>{{ unreadEvents.length }} {{ localeStore.t('alerts.unread') }}</h3>
      </div>
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

header {
  margin-bottom: 14px;
}

h3,
p,
strong {
  margin: 0;
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
  padding: 14px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.03);
}

.event-row p,
.empty-state {
  color: var(--text-secondary);
}

button {
  border: 1px solid var(--border);
  border-radius: 10px;
  background: transparent;
  color: var(--text);
  padding: 10px 12px;
  cursor: pointer;
}
</style>
