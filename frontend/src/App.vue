<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { RouterLink, RouterView, useRoute } from 'vue-router'

import ProviderBadge from '@/components/ProviderBadge.vue'
import { useSystemStore } from '@/stores/system'
import { buildProviderBadgeLabel, buildRuntimeSummary, getHealthHeadline } from '@/utils/runtime'

const route = useRoute()
const systemStore = useSystemStore()

const pageTitle = computed(() => {
  if (route.name === 'stock') return 'Stock Research'
  if (route.name === 'strategy-lab') return 'Strategy Lab'
  return 'Market Overview'
})

onMounted(() => {
  void systemStore.loadHealth()
})

const marketBadgeLabel = computed(() =>
  systemStore.health
    ? buildProviderBadgeLabel(systemStore.health.market_provider, systemStore.health.market_provider_status)
    : '',
)

const newsBadgeLabel = computed(() =>
  systemStore.health
    ? buildProviderBadgeLabel(systemStore.health.news_provider, systemStore.health.news_provider_status)
    : '',
)

const runtimeSummary = computed(() =>
  systemStore.health ? buildRuntimeSummary(systemStore.health) : '',
)

const healthHeadline = computed(() =>
  systemStore.health ? getHealthHeadline(systemStore.health) : '',
)
</script>

<template>
  <div class="app-shell">
    <header class="topbar page-shell">
      <div class="brand-lockup">
        <span class="eyebrow">Finance Quant Lab</span>
        <h1>{{ pageTitle }}</h1>
      </div>
      <nav>
        <RouterLink to="/">Overview</RouterLink>
        <RouterLink to="/stocks/US.AAPL">Stock Research</RouterLink>
        <RouterLink to="/strategy-lab">Strategy Lab</RouterLink>
      </nav>
      <div v-if="systemStore.health" class="status-zone">
        <div class="status-badges">
          <ProviderBadge :label="marketBadgeLabel" :status="systemStore.health.market_provider_status" />
          <ProviderBadge :label="newsBadgeLabel" :status="systemStore.health.news_provider_status" />
        </div>
        <div class="status-copy">
          <span class="mono">{{ runtimeSummary }}</span>
          <span class="status-headline">{{ healthHeadline }}</span>
        </div>
      </div>
    </header>

    <main class="page-shell">
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
.app-shell {
  min-height: 100vh;
}

.topbar {
  position: sticky;
  top: 0;
  z-index: 10;
  display: grid;
  grid-template-columns: 1.4fr 1fr auto;
  align-items: center;
  gap: 24px;
  padding-top: 24px;
  padding-bottom: 24px;
  backdrop-filter: blur(14px);
}

.brand-lockup h1 {
  margin: 6px 0 0;
  font-family: 'Chakra Petch', sans-serif;
  font-size: clamp(1.8rem, 2vw, 2.5rem);
}

nav {
  display: flex;
  gap: 12px;
  justify-content: center;
}

nav a {
  padding: 12px 16px;
  border-radius: 999px;
  color: var(--text-secondary);
  border: 1px solid transparent;
  transition: all 180ms ease;
}

nav a.router-link-active {
  color: var(--text);
  border-color: var(--border);
  background: rgba(255, 255, 255, 0.04);
}

.status-zone {
  display: grid;
  justify-items: end;
  gap: 8px;
}

.status-badges {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 10px;
}

.status-copy {
  display: grid;
  gap: 4px;
  max-width: 440px;
  text-align: right;
  color: var(--text-muted);
}

.status-headline {
  color: var(--text-secondary);
}

@media (max-width: 1024px) {
  .topbar {
    grid-template-columns: 1fr;
  }

  nav,
  .status-zone {
    justify-content: flex-start;
  }

  .status-zone,
  .status-copy,
  .status-badges {
    justify-items: start;
    justify-content: flex-start;
    text-align: left;
  }
}
</style>
