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

const pageMeta = computed(() => {
  if (route.name === 'stock') {
    const symbol = String(route.params.symbol ?? 'HK.00700')
    return {
      eyebrow: localeStore.t('common.stockResearch'),
      title: symbol,
      summary:
        localeStore.locale === 'zh-CN'
          ? '围绕单一标的快速形成判断，再决定是否加入观察、设置提醒或进入策略验证。'
          : 'Form a view on one symbol quickly, then decide whether to watch it, alert on it, or move into validation.',
      focus: localeStore.locale === 'zh-CN' ? '结论优先' : 'Thesis First',
    }
  }

  if (route.name === 'strategy-lab') {
    return {
      eyebrow: localeStore.t('common.strategyLab'),
      title: localeStore.t('strategy.runResults'),
      summary: localeStore.t('strategy.description'),
      focus:
        localeStore.locale === 'zh-CN'
          ? '配置 → 解释 → 对比'
          : 'Configure -> Explain -> Compare',
    }
  }

  return {
    eyebrow: localeStore.t('common.marketOverview'),
    title: localeStore.t('overview.opportunityBoard'),
    summary: localeStore.t('overview.description'),
    focus:
      localeStore.locale === 'zh-CN'
        ? '先判断环境，再锁定候选'
        : 'Frame the market, then lock candidates',
  }
})
</script>

<template>
  <div class="app-shell">
    <aside class="desk-rail">
      <div class="rail-brand glass-line">
        <span class="eyebrow">{{ localeStore.t('shell.eyebrow') }}</span>
        <strong>Finance Quant Lab</strong>
        <p class="muted">
          {{ localeStore.locale === 'zh-CN' ? '机构化研究工作台' : 'Institutional research workstation' }}
        </p>
      </div>

      <nav class="rail-nav glass-line">
        <RouterLink to="/">
          <span class="eyebrow">{{ localeStore.t('common.marketOverview') }}</span>
          <strong>{{ localeStore.t('overview.opportunityBoard') }}</strong>
        </RouterLink>
        <RouterLink to="/stocks/HK.00700">
          <span class="eyebrow">{{ localeStore.t('common.stockResearch') }}</span>
          <strong>{{ localeStore.t('common.whyWatch') }}</strong>
        </RouterLink>
        <RouterLink to="/strategy-lab">
          <span class="eyebrow">{{ localeStore.t('common.strategyLab') }}</span>
          <strong>{{ localeStore.t('strategy.tradeMarkers') }}</strong>
        </RouterLink>
      </nav>

      <div v-if="systemStore.health" class="rail-status glass-line">
        <div class="rail-status__head">
          <span class="eyebrow">{{ pageTitle }}</span>
          <strong>{{ healthHeadline }}</strong>
        </div>
        <div class="rail-status__badges">
          <ProviderBadge :label="marketBadgeLabel" :status="systemStore.health.market_provider_status" />
          <ProviderBadge :label="newsBadgeLabel" :status="systemStore.health.news_provider_status" />
        </div>
        <p class="mono muted">{{ runtimeSummary }}</p>
      </div>

      <div class="rail-tools glass-line">
        <LocaleSwitcher />
      </div>
    </aside>

    <div class="desk-stage">
      <header class="desk-context page-shell">
        <div class="desk-context__copy">
          <span class="eyebrow">{{ pageMeta.eyebrow }}</span>
          <div class="desk-context__title-row">
            <h1>{{ pageMeta.title }}</h1>
            <span class="context-focus">{{ pageMeta.focus }}</span>
          </div>
          <p>{{ pageMeta.summary }}</p>
        </div>

        <div class="desk-context__search">
          <StockCodeSearch />
        </div>

        <div v-if="systemStore.health" class="desk-context__status glass-line">
          <span class="eyebrow">{{ localeStore.locale === 'zh-CN' ? '工作区状态' : 'Workspace Status' }}</span>
          <strong>{{ pageTitle }}</strong>
          <p>{{ healthHeadline }}</p>
          <span class="mono">{{ runtimeSummary }}</span>
        </div>
      </header>

      <main class="page-shell">
        <RouterView />
      </main>
    </div>
  </div>
</template>

<style scoped>
.app-shell {
  min-height: 100vh;
  display: grid;
  grid-template-columns: 280px minmax(0, 1fr);
}

.desk-rail {
  position: sticky;
  top: 0;
  align-self: start;
  min-height: 100vh;
  padding: 28px 18px 24px 22px;
  display: grid;
  gap: 18px;
}

.rail-brand,
.rail-nav,
.rail-status,
.rail-tools,
.desk-context__status {
  border-radius: 24px;
  padding: 18px;
  backdrop-filter: blur(16px);
}

.rail-brand,
.rail-status,
.rail-tools,
.desk-context__status {
  display: grid;
  gap: 10px;
}

.rail-brand strong {
  font-size: 1.35rem;
  font-family: 'Chakra Petch', sans-serif;
}

.rail-brand p {
  margin: 0;
}

.rail-nav {
  display: grid;
  gap: 10px;
}

.rail-nav a {
  display: grid;
  gap: 8px;
  padding: 14px 16px;
  border-radius: 18px;
  color: var(--text-secondary);
  border: 1px solid transparent;
  background: rgba(255, 255, 255, 0.02);
}

.rail-nav strong {
  font-size: 1rem;
  font-weight: 600;
}

.rail-nav a.router-link-active {
  color: var(--text);
  border-color: var(--border-strong);
  background:
    linear-gradient(180deg, rgba(70, 212, 255, 0.14), rgba(255, 255, 255, 0.03)),
    rgba(255, 255, 255, 0.03);
  box-shadow: 0 0 0 1px rgba(70, 212, 255, 0.08);
}

.rail-status__head {
  display: grid;
  gap: 6px;
}

.rail-status__head strong {
  font-size: 1rem;
}

.rail-status__badges {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.desk-stage {
  min-width: 0;
}

.desk-context {
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) minmax(360px, 0.85fr) 280px;
  gap: 18px;
  align-items: stretch;
  padding-top: 22px;
  padding-bottom: 0;
}

.desk-context__copy {
  display: grid;
  align-content: start;
  gap: 10px;
}

.desk-context__title-row {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.desk-context__copy h1 {
  margin: 0;
  font-size: clamp(1.9rem, 2.2vw, 3rem);
  font-family: 'Chakra Petch', sans-serif;
  line-height: 0.95;
}

.desk-context__copy p,
.desk-context__status p {
  margin: 0;
  color: var(--text-secondary);
  line-height: 1.55;
}

.context-focus {
  display: inline-flex;
  align-items: center;
  padding: 8px 12px;
  border-radius: 999px;
  border: 1px solid var(--border);
  color: var(--accent);
  background: var(--accent-soft);
  font-size: 0.78rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.desk-context__search {
  display: grid;
  align-items: end;
}

.desk-context__status strong {
  font-size: 1rem;
}

@media (max-width: 1260px) {
  .app-shell {
    grid-template-columns: 1fr;
  }

  .desk-rail {
    position: static;
    min-height: 0;
    padding: 18px 18px 0;
  }

  .rail-nav {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .desk-context {
    grid-template-columns: 1fr;
    padding-top: 18px;
  }
}

@media (max-width: 860px) {
  .rail-nav {
    grid-template-columns: 1fr;
  }
}
</style>
