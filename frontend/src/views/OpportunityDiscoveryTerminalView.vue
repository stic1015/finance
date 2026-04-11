<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import { apiGet } from '@/api/client'
import AlertCenter from '@/components/AlertCenter.vue'
import MetricTile from '@/components/MetricTile.vue'
import NewsCard from '@/components/NewsCard.vue'
import ProviderBadge from '@/components/ProviderBadge.vue'
import RankedSymbolTableClean from '@/components/RankedSymbolTableClean.vue'
import SectionPanel from '@/components/SectionPanel.vue'
import { useLocaleStore } from '@/stores/locale'
import { useSystemStore } from '@/stores/system'
import { useWatchStore } from '@/stores/watch'
import type { MarketOverview, NewsFeedResponse } from '@/types'
import { formatMarketPercent } from '@/utils/format'
import { buildLocalizedProviderBadgeLabel, buildLocalizedRuntimeSummary, translateStatus } from '@/utils/presentation'

const localeStore = useLocaleStore()
const systemStore = useSystemStore()
const watchStore = useWatchStore()

const overview = ref<MarketOverview | null>(null)
const marketBriefs = ref<NewsFeedResponse | null>(null)
const loadingOverview = ref(false)
const overviewError = ref('')
const loadingBriefs = ref(false)
const briefsError = ref('')
const filter = ref<'all' | 'live' | 'news' | 'backtest'>('all')

async function loadOverview() {
  loadingOverview.value = true
  overviewError.value = ''
  try {
    overview.value = await apiGet<MarketOverview>('/api/markets/overview')
  } catch (err) {
    overviewError.value = err instanceof Error ? err.message : localeStore.t('common.loading')
  } finally {
    loadingOverview.value = false
  }
}

async function loadBriefs() {
  loadingBriefs.value = true
  briefsError.value = ''
  try {
    marketBriefs.value = await apiGet<NewsFeedResponse>('/api/markets/briefs')
  } catch (err) {
    briefsError.value = err instanceof Error ? err.message : localeStore.t('overview.briefsError')
  } finally {
    loadingBriefs.value = false
  }
}

onMounted(() => {
  void loadOverview()
  void loadBriefs()
  if (!systemStore.health) {
    void systemStore.loadHealth()
  }
})

const sections = computed(() => overview.value?.sections.filter((section) => section.region !== 'US') ?? [])
const watchlist = computed(() => overview.value?.watchlist ?? [])
const briefItems = computed(() => marketBriefs.value?.items ?? [])
const runtimeSummary = computed(() => (systemStore.health ? buildLocalizedRuntimeSummary(systemStore.health) : ''))

const filteredWatchlist = computed(() =>
  watchlist.value.filter((item) => {
    if (filter.value === 'live') return item.source_status === 'live'
    if (filter.value === 'news') {
      return briefItems.value.some((news) =>
        news.matched_symbols.some((match) => item.symbol.startsWith(`${match}.`) || item.symbol.startsWith(match)),
      )
    }
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
    avg_change:
      section.metrics.reduce((sum, metric) => sum + metric.change_percent, 0) / Math.max(section.metrics.length, 1),
  })),
)

const liveCount = computed(() => watchlist.value.filter((item) => item.source_status === 'live').length)

const summaryTiles = computed(() => [
  {
    label: localeStore.t('overview.liveCoverage'),
    value: `${liveCount.value}/${watchlist.value.length || 0}`,
  },
  {
    label: localeStore.t('overview.marketBriefs'),
    value: String(briefItems.value.length),
  },
  {
    label: localeStore.t('overview.watchGroups'),
    value: String(watchStore.groups.length),
  },
])
</script>

<template>
  <div class="overview-layout">
    <section v-if="overview" class="overview-toolbar panel">
      <div class="toolbar-copy">
        <div class="eyebrow">{{ localeStore.t('overview.eyebrow') }}</div>
        <h2>{{ localeStore.t('overview.opportunityBoard') }}</h2>
        <p>{{ localeStore.t('overview.description') }}</p>
      </div>
      <div class="toolbar-status">
        <ProviderBadge
          :label="buildLocalizedProviderBadgeLabel(overview.provider, overview.source_status)"
          :status="overview.source_status"
        />
        <span class="mono">{{ localeStore.t('overview.updatedAt') }} {{ new Date(overview.generated_at).toLocaleString() }}</span>
        <span class="mono">{{ runtimeSummary }}</span>
      </div>
      <div class="toolbar-metrics">
        <MetricTile v-for="tile in summaryTiles" :key="tile.label" :label="tile.label" :value="tile.value" />
      </div>
    </section>

    <div v-if="loadingOverview" class="panel loading-block">{{ localeStore.t('common.loading') }}</div>
    <div v-else-if="overviewError" class="panel loading-block error">{{ overviewError }}</div>

    <template v-else-if="overview">
      <div class="overview-main-grid">
        <div class="main-column">
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
              <SectionPanel :title="localeStore.t('overview.hotList')" :subtitle="''">
                <RankedSymbolTableClean :items="hotList" />
              </SectionPanel>

              <SectionPanel :title="localeStore.t('overview.movers')" :subtitle="''">
                <RankedSymbolTableClean :items="movers" />
              </SectionPanel>
            </div>
          </SectionPanel>

          <SectionPanel :title="localeStore.t('overview.sectorStrength')" :subtitle="localeStore.t('overview.marketPulse')">
            <div class="sector-grid">
              <article v-for="sector in sectorStrength" :key="sector.region" class="sector-card panel">
                <div class="sector-top">
                  <div class="eyebrow">{{ sector.title }}</div>
                  <ProviderBadge :label="translateStatus(sector.source_status)" :status="sector.source_status" />
                </div>
                <strong>{{ formatMarketPercent(sector.avg_change) }}</strong>
                <p class="muted">{{ sector.region }}</p>
              </article>
            </div>
          </SectionPanel>

          <SectionPanel :title="localeStore.t('overview.currentWatchlist')" :subtitle="localeStore.t('overview.watchGroups')">
            <div class="watchlist-grid">
              <article v-for="group in watchStore.groups" :key="group.id" class="watch-card panel">
                <div class="eyebrow">{{ group.name }}</div>
                <strong>{{ group.symbols.length }}</strong>
                <p class="muted">{{ group.symbols.join(' / ') }}</p>
              </article>
            </div>
          </SectionPanel>
        </div>

        <aside class="side-column">
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

          <SectionPanel :title="localeStore.t('overview.marketBriefs')" :subtitle="localeStore.t('overview.briefsAsync')">
            <div v-if="loadingBriefs" class="brief-state panel">{{ localeStore.t('overview.briefsLoading') }}</div>
            <div v-else-if="briefsError" class="brief-state panel error">{{ briefsError }}</div>
            <div v-else-if="briefItems.length" class="news-grid">
              <NewsCard v-for="item in briefItems" :key="item.id" :item="item" />
            </div>
            <div v-else class="brief-state panel">{{ localeStore.t('overview.briefsEmpty') }}</div>
          </SectionPanel>
        </aside>
      </div>
    </template>
  </div>
</template>

<style scoped>
.overview-layout,
.toolbar-metrics,
.content-grid,
.metrics-grid,
.news-grid,
.watchlist-grid,
.sector-grid {
  display: grid;
  gap: 20px;
}

.overview-toolbar {
  display: grid;
  grid-template-columns: minmax(0, 1.3fr) auto;
  gap: 20px;
  padding: 22px 26px;
}

.toolbar-copy h2 {
  margin: 8px 0 10px;
  font-size: clamp(1.4rem, 2vw, 2rem);
  font-family: 'Chakra Petch', sans-serif;
}

.toolbar-copy p {
  margin: 0;
  max-width: 760px;
  color: var(--text-secondary);
  line-height: 1.55;
}

.toolbar-status {
  display: grid;
  justify-items: end;
  align-content: start;
  gap: 8px;
}

.toolbar-metrics {
  grid-column: 1 / -1;
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.toolbar-metrics :deep(.metric-tile) {
  min-height: 0;
  padding: 14px 16px;
}

.toolbar-metrics :deep(strong) {
  font-size: 1.45rem;
}

.overview-main-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.6fr) 360px;
  gap: 20px;
}

.main-column,
.side-column {
  display: grid;
  gap: 20px;
}

.content-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.metrics-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.watch-card,
.sector-card {
  display: grid;
  gap: 10px;
  padding: 16px;
}

.sector-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
}

.watch-card strong,
.sector-card strong {
  font-size: 1.45rem;
  font-family: 'Chakra Petch', sans-serif;
}

.filter-group {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.filter-group button {
  border: 1px solid var(--border);
  border-radius: 999px;
  background: transparent;
  color: var(--text-secondary);
  padding: 8px 12px;
  cursor: pointer;
}

.filter-group button.active {
  color: var(--text);
  border-color: var(--border-strong);
}

.brief-state,
.loading-block {
  padding: 20px;
}

.error {
  color: var(--negative);
}

@media (max-width: 1200px) {
  .overview-toolbar,
  .overview-main-grid,
  .content-grid,
  .toolbar-metrics,
  .metrics-grid {
    grid-template-columns: 1fr;
  }

  .toolbar-status {
    justify-items: start;
  }
}
</style>
