<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'

import { apiGet } from '@/api/client'
import AlertCenter from '@/components/AlertCenter.vue'
import MetricTile from '@/components/MetricTile.vue'
import NewsCard from '@/components/NewsCard.vue'
import ProviderBadge from '@/components/ProviderBadge.vue'
import RankedSymbolTable from '@/components/RankedSymbolTable.vue'
import SectionPanel from '@/components/SectionPanel.vue'
import { useLocaleStore } from '@/stores/locale'
import { useSystemStore } from '@/stores/system'
import { useWatchStore } from '@/stores/watch'
import type { MarketOverview, NewsFeedResponse } from '@/types'
import { compactNumber, formatCurrency, formatMarketPercent } from '@/utils/format'
import { buildLocalizedProviderBadgeLabel, buildLocalizedRuntimeSummary, translateStatus } from '@/utils/presentation'

const localeStore = useLocaleStore()
const systemStore = useSystemStore()
const watchStore = useWatchStore()
const overview = ref<MarketOverview | null>(null)
const marketBriefs = ref<NewsFeedResponse | null>(null)
const loading = ref(false)
const error = ref('')
const filter = ref<'all' | 'live' | 'news' | 'backtest'>('all')

async function loadOverview() {
  loading.value = true
  error.value = ''
  try {
    const [overviewResponse, briefsResponse] = await Promise.all([
      apiGet<MarketOverview>('/api/markets/overview'),
      apiGet<NewsFeedResponse>('/api/markets/briefs'),
    ])
    overview.value = overviewResponse
    marketBriefs.value = briefsResponse
  } catch (err) {
    error.value = err instanceof Error ? err.message : localeStore.t('common.loading')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  void loadOverview()
  if (!systemStore.health) {
    void systemStore.loadHealth()
  }
})

const sections = computed(() => overview.value?.sections.filter((section) => section.region !== 'US') ?? [])
const watchlist = computed(() => overview.value?.watchlist ?? [])
const filteredWatchlist = computed(() =>
  watchlist.value.filter((item) => {
    if (filter.value === 'live') return item.source_status === 'live'
    if (filter.value === 'news') return (overview.value?.top_news ?? []).some((news) => news.matched_symbols.includes(item.symbol))
    if (filter.value === 'backtest') return item.source_status !== 'unavailable'
    return true
  }),
)
const hotList = computed(() =>
  [...filteredWatchlist.value].sort((a, b) => Math.abs(b.change_percent) - Math.abs(a.change_percent)).slice(0, 30),
)
const movers = computed(() =>
  [...filteredWatchlist.value].sort((a, b) => b.change_percent - a.change_percent).slice(0, 30),
)
const sectorStrength = computed(() =>
  sections.value.map((section) => ({
    region: section.region,
    title: section.title,
    source_status: section.source_status,
    avg_change: section.metrics.reduce((sum, metric) => sum + metric.change_percent, 0) / Math.max(section.metrics.length, 1),
  })),
)
const runtimeSummary = computed(() => (systemStore.health ? buildLocalizedRuntimeSummary(systemStore.health) : ''))

function addToWatch(symbol: string) {
  watchStore.addSymbol(symbol)
}
</script>

<template>
  <div class="overview-layout">
    <section class="hero panel">
      <div>
        <div class="eyebrow">{{ localeStore.t('overview.eyebrow') }}</div>
        <h2>{{ localeStore.t('overview.title') }}</h2>
        <p>{{ localeStore.t('overview.description') }}</p>
      </div>
      <div class="hero-meta" v-if="overview && systemStore.health">
        <ProviderBadge :label="buildLocalizedProviderBadgeLabel(overview.provider, overview.source_status)" :status="overview.source_status" />
        <span class="mono">{{ localeStore.t('overview.updatedAt') }} {{ new Date(overview.generated_at).toLocaleString() }}</span>
        <span class="mono">{{ runtimeSummary }}</span>
      </div>
    </section>

    <div v-if="loading" class="panel loading-block">{{ localeStore.t('common.loading') }}</div>
    <div v-else-if="error" class="panel loading-block error">{{ error }}</div>

    <template v-else-if="overview">
      <div class="top-grid">
        <SectionPanel :title="localeStore.t('overview.dataTrust')" :subtitle="localeStore.t('common.marketOverview')">
          <div class="metrics-grid">
            <MetricTile
              :label="localeStore.t('shell.storage')"
              :value="systemStore.health?.database_mode === 'memory' ? localeStore.t('common.simulated') : 'SQLite'"
            />
            <MetricTile
              :label="localeStore.t('shell.jobs')"
              :value="systemStore.health?.executor_mode === 'thread_pool' ? localeStore.t('shell.threadPool') : localeStore.t('shell.processPool')"
            />
            <MetricTile
              :label="localeStore.t('overview.hkSession')"
              :value="translateStatus(sections.find((item) => item.region === 'HK')?.source_status ?? 'unavailable')"
            />
            <MetricTile
              :label="localeStore.t('overview.cnSession')"
              :value="translateStatus(sections.find((item) => item.region === 'CN')?.source_status ?? 'unavailable')"
            />
          </div>
        </SectionPanel>
        <AlertCenter />
      </div>

      <SectionPanel :title="localeStore.t('overview.opportunityBoard')" :subtitle="localeStore.t('common.discoverOpportunities')">
        <template #actions>
          <div class="filter-group">
            <button type="button" :class="{ active: filter === 'all' }" @click="filter = 'all'">{{ localeStore.t('common.all') }}</button>
            <button type="button" :class="{ active: filter === 'live' }" @click="filter = 'live'">{{ localeStore.t('overview.onlyRealtime') }}</button>
            <button type="button" :class="{ active: filter === 'news' }" @click="filter = 'news'">{{ localeStore.t('overview.onlyWithNews') }}</button>
            <button type="button" :class="{ active: filter === 'backtest' }" @click="filter = 'backtest'">{{ localeStore.t('overview.onlyBacktestReady') }}</button>
          </div>
        </template>

        <div class="content-grid">
          <SectionPanel :title="localeStore.t('overview.hotList')">
            <RankedSymbolTable :items="hotList" />
          </SectionPanel>

          <SectionPanel :title="localeStore.t('overview.movers')">
            <RankedSymbolTable :items="movers" />
          </SectionPanel>

          <SectionPanel :title="localeStore.t('overview.sectorStrength')">
            <div class="watchlist-grid">
              <article v-for="sector in sectorStrength" :key="sector.region" class="watch-card panel">
                <div class="watch-top">
                  <div class="eyebrow">{{ sector.title }}</div>
                  <ProviderBadge :label="translateStatus(sector.source_status)" :status="sector.source_status" />
                </div>
                <strong>{{ formatMarketPercent(sector.avg_change) }}</strong>
                <p class="muted">{{ sector.region }}</p>
              </article>
            </div>
          </SectionPanel>
        </div>
      </SectionPanel>

      <div class="bottom-grid">
        <SectionPanel :title="localeStore.t('overview.currentWatchlist')" :subtitle="localeStore.t('overview.watchGroups')">
          <div class="watchlist-grid">
            <article v-for="group in watchStore.groups" :key="group.id" class="watch-card panel">
              <div class="eyebrow">{{ group.name }}</div>
              <strong>{{ group.symbols.length }}</strong>
              <p class="muted">{{ group.symbols.join(' / ') }}</p>
            </article>
          </div>
        </SectionPanel>

        <SectionPanel :title="localeStore.t('overview.relatedNews')" :subtitle="localeStore.t('overview.latestClues')">
          <div v-if="overview.top_news.length" class="news-grid">
            <NewsCard v-for="item in overview.top_news" :key="item.id" :item="item" />
          </div>
          <div v-else class="panel loading-block">{{ localeStore.t('common.noAttributedNews') }}</div>
        </SectionPanel>

        <SectionPanel title="行业实时快讯" subtitle="市场与行业层面的快速线索">
          <div v-if="marketBriefs?.items.length" class="news-grid">
            <NewsCard v-for="item in marketBriefs.items" :key="item.id" :item="item" />
          </div>
          <div v-else class="panel loading-block">当前暂无行业快讯。</div>
        </SectionPanel>
      </div>
    </template>
  </div>
</template>

<style scoped>
.overview-layout,
.top-grid,
.content-grid,
.bottom-grid,
.metrics-grid,
.watchlist-grid,
.news-grid {
  display: grid;
  gap: 20px;
}

.hero {
  display: grid;
  grid-template-columns: 1.2fr auto;
  gap: 24px;
  align-items: end;
  padding: 24px 30px;
}

.hero h2 {
  max-width: 760px;
  margin: 10px 0 12px;
  font-size: clamp(2rem, 4vw, 3rem);
  line-height: 0.98;
  font-family: 'Chakra Petch', sans-serif;
}

.hero p {
  max-width: 720px;
  margin: 0;
  color: var(--text-secondary);
  line-height: 1.6;
}

.hero-meta {
  display: grid;
  justify-items: end;
  gap: 10px;
}

.top-grid {
  grid-template-columns: 1.2fr 0.8fr;
}

.content-grid {
  grid-template-columns: 1.1fr 1.1fr 0.8fr;
}

.bottom-grid {
  grid-template-columns: 0.75fr 1fr 1fr;
}

.metrics-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.watch-card {
  display: grid;
  gap: 10px;
  padding: 16px;
}

.watch-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
}

.watch-card strong {
  font-size: 1.45rem;
  font-family: 'Chakra Petch', sans-serif;
}

.filter-group {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.filter-group button,
.watch-card button {
  border: 1px solid var(--border);
  border-radius: 999px;
  background: transparent;
  color: var(--text-secondary);
  padding: 10px 12px;
  cursor: pointer;
}

.filter-group button.active {
  color: var(--text);
  border-color: var(--border-strong);
}

.loading-block {
  padding: 22px;
}

.error {
  color: var(--negative);
}

@media (max-width: 1200px) {
  .hero,
  .top-grid,
  .content-grid,
  .bottom-grid,
  .metrics-grid {
    grid-template-columns: 1fr;
  }

  .hero-meta {
    justify-items: start;
  }
}
</style>
