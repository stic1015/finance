<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { RouterLink, RouterView, useRoute } from 'vue-router'

import LocaleSwitcher from '@/components/LocaleSwitcher.vue'
import ProviderBadge from '@/components/ProviderBadge.vue'
import StockCodeSearch from '@/components/StockCodeSearch.vue'
import { useLocaleStore } from '@/stores/locale'
import { useSystemStore } from '@/stores/system'
import {
  buildLocalizedProviderBadgeLabel,
  buildLocalizedRuntimeSummary,
  getLocalizedHealthHeadline,
} from '@/utils/presentation'

const route = useRoute()
const localeStore = useLocaleStore()
const systemStore = useSystemStore()

const pageTitle = computed(() => {
  if (route.name === 'stock') return localeStore.t('common.stockResearch')
  if (route.name === 'strategy-lab') return localeStore.t('common.strategyLab')
  return localeStore.t('common.marketOverview')
})

onMounted(() => {
  void systemStore.loadHealth()
})

const marketBadgeLabel = computed(() =>
  systemStore.health
    ? buildLocalizedProviderBadgeLabel(systemStore.health.market_provider, systemStore.health.market_provider_status)
    : '',
)

const newsBadgeLabel = computed(() =>
  systemStore.health
    ? buildLocalizedProviderBadgeLabel(systemStore.health.news_provider, systemStore.health.news_provider_status)
    : '',
)

const runtimeSummary = computed(() =>
  systemStore.health ? buildLocalizedRuntimeSummary(systemStore.health) : '',
)

const healthHeadline = computed(() =>
  systemStore.health ? getLocalizedHealthHeadline(systemStore.health) : '',
)
</script>

<template>
  <div class="app-shell">
    <header class="topbar page-shell">
      <div class="brand-lockup">
        <span class="eyebrow">{{ localeStore.t('shell.eyebrow') }}</span>
        <h1>{{ pageTitle }}</h1>
      </div>
      <StockCodeSearch />
      <nav>
        <RouterLink to="/">{{ localeStore.t('common.marketOverview') }}</RouterLink>
        <RouterLink to="/stocks/HK.00700">{{ localeStore.t('common.stockResearch') }}</RouterLink>
        <RouterLink to="/strategy-lab">{{ localeStore.t('common.strategyLab') }}</RouterLink>
      </nav>
      <div class="status-zone">
        <LocaleSwitcher />
        <div v-if="systemStore.health" class="status-stack">
          <div class="status-badges">
            <ProviderBadge :label="marketBadgeLabel" :status="systemStore.health.market_provider_status" />
            <ProviderBadge :label="newsBadgeLabel" :status="systemStore.health.news_provider_status" />
          </div>
          <div class="status-copy">
            <span class="mono">{{ runtimeSummary }}</span>
            <span class="status-headline">{{ healthHeadline }}</span>
          </div>
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
  grid-template-columns: 0.9fr 1fr 0.8fr auto;
  align-items: center;
  gap: 12px;
  padding-top: 12px;
  padding-bottom: 12px;
  backdrop-filter: blur(14px);
}

.brand-lockup h1 {
  margin: 4px 0 0;
  font-family: 'Chakra Petch', sans-serif;
  font-size: clamp(1.15rem, 1.3vw, 1.55rem);
}

nav {
  display: flex;
  gap: 12px;
  justify-content: center;
}

nav a {
  padding: 9px 14px;
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
  gap: 6px;
  justify-items: end;
}

.status-stack {
  display: grid;
  gap: 6px;
  justify-items: end;
}

.status-badges {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 10px;
}

.status-copy {
  display: grid;
  gap: 2px;
  max-width: 360px;
  text-align: right;
  color: var(--text-muted);
  font-size: 0.85rem;
}

.status-headline {
  color: var(--text-secondary);
}

@media (max-width: 1024px) {
  .topbar {
    grid-template-columns: 1fr;
  }

  nav,
  .status-zone,
  .status-stack,
  .status-copy,
  .status-badges {
    justify-content: flex-start;
    justify-items: start;
    text-align: left;
  }
}
</style>
