<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import { apiGet } from '@/api/client'
import AlertCenter from '@/components/AlertCenter.vue'
import MetricTile from '@/components/MetricTile.vue'
import NewsCard from '@/components/NewsCard.vue'
import ProviderBadge from '@/components/ProviderBadge.vue'
import SectionPanel from '@/components/SectionPanel.vue'
import { useLocaleStore } from '@/stores/locale'
import { useSystemStore } from '@/stores/system'
import { useWatchStore } from '@/stores/watch'
import type { MarketOpportunities, MarketOverview, OpportunityAction } from '@/types'
import type { NewsFeedResponse } from '@/types'
import { formatMarketPercent } from '@/utils/format'
import { buildLocalizedProviderBadgeLabel, buildLocalizedRuntimeSummary, translateStatus } from '@/utils/presentation'

const localeStore = useLocaleStore()
const systemStore = useSystemStore()
const watchStore = useWatchStore()

const overview = ref<MarketOverview | null>(null)
const opportunities = ref<MarketOpportunities | null>(null)
const marketBriefs = ref<NewsFeedResponse | null>(null)

const loading = ref(false)
const error = ref('')
const loadingBriefs = ref(false)
const briefsError = ref('')
const actionFilter = ref<'all' | OpportunityAction>('all')

const scanLimit = 60

async function loadOverview() {
  overview.value = await apiGet<MarketOverview>('/api/markets/overview')
}

async function loadOpportunities() {
  opportunities.value = await apiGet<MarketOpportunities>(`/api/markets/opportunities?markets=HK,CN&limit=${scanLimit}`)
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

async function loadAll() {
  loading.value = true
  error.value = ''
  try {
    await Promise.all([loadOverview(), loadOpportunities(), loadBriefs()])
  } catch (err) {
    error.value = err instanceof Error ? err.message : localeStore.t('common.loading')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  void loadAll()
  if (!systemStore.health) {
    void systemStore.loadHealth()
  }
})

const briefItems = computed(() => marketBriefs.value?.items ?? [])
const runtimeSummary = computed(() => (systemStore.health ? buildLocalizedRuntimeSummary(systemStore.health) : ''))
const watchGroupPreview = computed(() => watchStore.groups.slice(0, 4))
const sections = computed(() => overview.value?.sections.filter((section) => section.region !== 'US') ?? [])

const filteredItems = computed(() => {
  const items = opportunities.value?.items ?? []
  if (actionFilter.value === 'all') return items
  return items.filter((item) => item.action === actionFilter.value)
})

const buyCount = computed(() => opportunities.value?.items.filter((item) => item.action === 'buy').length ?? 0)
const watchCount = computed(() => opportunities.value?.items.filter((item) => item.action === 'watch').length ?? 0)
const avoidCount = computed(() => opportunities.value?.items.filter((item) => item.action === 'avoid').length ?? 0)

const summaryTiles = computed(() => [
  {
    label: localeStore.t('overview.universe'),
    value: String(opportunities.value?.universe_size ?? 0),
  },
  {
    label: localeStore.t('overview.scanned'),
    value: String(opportunities.value?.scanned_size ?? 0),
  },
  {
    label: localeStore.t('overview.actionBuy'),
    value: String(buyCount.value),
  },
  {
    label: localeStore.t('overview.actionWatch'),
    value: String(watchCount.value),
  },
])

function actionLabel(action: OpportunityAction) {
  if (action === 'buy') return localeStore.t('overview.actionBuy')
  if (action === 'watch') return localeStore.t('overview.actionWatch')
  return localeStore.t('overview.actionAvoid')
}

function actionClass(action: OpportunityAction) {
  if (action === 'buy') return 'status-positive'
  if (action === 'watch') return 'status-neutral'
  return 'status-negative'
}
</script>

<template>
  <div class="overview-layout">
    <section v-if="opportunities" class="pulse-hero panel">
      <div class="pulse-copy">
        <div class="eyebrow">{{ localeStore.t('overview.eyebrow') }}</div>
        <h2>{{ localeStore.t('overview.singleBoardTitle') }}</h2>
        <p>{{ localeStore.t('overview.singleBoardSubtitle') }}</p>
        <div class="pulse-meta">
          <ProviderBadge
            :label="buildLocalizedProviderBadgeLabel(opportunities.provider, opportunities.source_status)"
            :status="opportunities.source_status"
          />
          <span class="mono">{{ localeStore.t('overview.updatedAt') }} {{ new Date(opportunities.generated_at).toLocaleString() }}</span>
          <span class="mono">{{ localeStore.t('overview.refreshHint') }}</span>
          <span class="mono">{{ runtimeSummary }}</span>
        </div>
      </div>
      <div class="pulse-metrics">
        <MetricTile v-for="tile in summaryTiles" :key="tile.label" :label="tile.label" :value="tile.value" />
      </div>
    </section>

    <div v-if="loading" class="panel empty-shell">{{ localeStore.t('common.loading') }}</div>
    <div v-else-if="error" class="panel empty-shell error">{{ error }}</div>

    <template v-else-if="opportunities">
      <div class="overview-main-grid">
        <div class="main-column">
          <SectionPanel :title="localeStore.t('overview.singleBoardTitle')" :subtitle="localeStore.t('common.discoverOpportunities')">
            <template #actions>
              <div class="filter-group">
                <button type="button" class="interactive-chip" :class="{ active: actionFilter === 'all' }" @click="actionFilter = 'all'">{{ localeStore.t('common.all') }}</button>
                <button type="button" class="interactive-chip" :class="{ active: actionFilter === 'buy' }" @click="actionFilter = 'buy'">{{ localeStore.t('overview.actionBuy') }}</button>
                <button type="button" class="interactive-chip" :class="{ active: actionFilter === 'watch' }" @click="actionFilter = 'watch'">{{ localeStore.t('overview.actionWatch') }}</button>
                <button type="button" class="interactive-chip" :class="{ active: actionFilter === 'avoid' }" @click="actionFilter = 'avoid'">{{ localeStore.t('overview.actionAvoid') }}</button>
              </div>
            </template>

            <div class="board-table panel">
              <table>
                <thead>
                  <tr>
                    <th>#</th>
                    <th>{{ localeStore.t('common.code') }}</th>
                    <th>{{ localeStore.t('common.name') }}</th>
                    <th>{{ localeStore.t('common.action') }}</th>
                    <th>{{ localeStore.t('overview.score') }}</th>
                    <th>{{ localeStore.t('overview.riskScore') }}</th>
                    <th>{{ localeStore.t('overview.reasons') }}</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(item, index) in filteredItems" :key="item.symbol">
                    <td>{{ index + 1 }}</td>
                    <td class="mono">
                      <RouterLink class="symbol-link" :to="`/stocks/${item.symbol}`">{{ item.symbol }}</RouterLink>
                    </td>
                    <td>
                      <RouterLink class="name-link" :to="`/stocks/${item.symbol}`">{{ item.display_name }}</RouterLink>
                    </td>
                    <td><span class="action-chip" :class="actionClass(item.action)">{{ actionLabel(item.action) }}</span></td>
                    <td>{{ item.score.toFixed(1) }}</td>
                    <td>{{ item.risk_score.toFixed(1) }}</td>
                    <td class="reason-cell">{{ item.reasons.slice(0, 2).join(' | ') }}</td>
                  </tr>
                </tbody>
              </table>
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
              <MetricTile :label="localeStore.t('overview.actionAvoid')" :value="String(avoidCount)" />
            </div>
          </SectionPanel>

          <AlertCenter />

          <SectionPanel :title="localeStore.t('overview.currentWatchlist')" :subtitle="localeStore.t('overview.watchGroups')">
            <div v-if="watchGroupPreview.length" class="watchlist-grid">
              <article v-for="group in watchGroupPreview" :key="group.id" class="watch-card glass-line">
                <div class="eyebrow">{{ group.name }}</div>
                <strong>{{ group.symbols.length }}</strong>
                <p class="muted">{{ group.symbols.join(' / ') }}</p>
              </article>
            </div>
            <div v-else class="tool-empty">No watch groups yet. Start from high-score candidates above.</div>
          </SectionPanel>

          <SectionPanel :title="localeStore.t('overview.marketBriefs')" :subtitle="localeStore.t('overview.briefsAsync')">
            <div v-if="loadingBriefs" class="tool-empty">{{ localeStore.t('overview.briefsLoading') }}</div>
            <div v-else-if="briefsError" class="tool-empty error">{{ briefsError }}</div>
            <div v-else-if="briefItems.length" class="news-grid">
              <NewsCard v-for="item in briefItems.slice(0, 4)" :key="item.id" :item="item" />
            </div>
            <div v-else class="tool-empty">{{ localeStore.t('overview.briefsEmpty') }}</div>
          </SectionPanel>
        </aside>
      </div>
    </template>
  </div>
</template>

<style scoped>
.overview-layout,
.pulse-metrics,
.metrics-grid,
.news-grid,
.watchlist-grid {
  display: grid;
  gap: 20px;
}

.pulse-hero {
  display: grid;
  grid-template-columns: minmax(0, 1.15fr) minmax(380px, 0.95fr);
  gap: 24px;
  padding: 26px;
}

.pulse-copy {
  display: grid;
  gap: 14px;
}

.pulse-copy h2 {
  margin: 8px 0 10px;
  font-size: clamp(2rem, 2.8vw, 3.2rem);
  font-family: 'Chakra Petch', sans-serif;
  line-height: 0.95;
}

.pulse-copy p {
  margin: 0;
  max-width: 720px;
  color: var(--text-secondary);
  line-height: 1.55;
}

.pulse-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 10px 12px;
  align-items: center;
}

.pulse-metrics {
  grid-template-columns: repeat(2, minmax(0, 1fr));
  align-self: stretch;
}

.pulse-metrics :deep(.metric-tile) {
  min-height: 138px;
}

.overview-main-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.65fr) 380px;
  gap: 22px;
}

.main-column,
.side-column {
  display: grid;
  gap: 22px;
}

.board-table {
  padding: 12px;
  overflow: auto;
  max-height: 780px;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th,
td {
  padding: 12px;
  border-bottom: 1px solid var(--border-subtle);
  text-align: left;
  white-space: nowrap;
}

th {
  font-size: 0.8rem;
  color: var(--text-muted);
  font-weight: 600;
}

.reason-cell {
  white-space: normal;
  min-width: 280px;
  color: var(--text-secondary);
}

.symbol-link,
.name-link {
  display: inline-flex;
  align-items: center;
  min-height: 24px;
}

.symbol-link {
  color: var(--accent);
}

.name-link {
  font-weight: 500;
}

.action-chip {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 28px;
  padding: 4px 10px;
  border-radius: 999px;
  border: 1px solid var(--border-subtle);
  font-size: 0.78rem;
  font-weight: 600;
}

.status-neutral {
  color: var(--accent);
  border-color: rgba(70, 212, 255, 0.45);
  background: rgba(70, 212, 255, 0.12);
}

.filter-group {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.watch-card {
  padding: 16px;
  display: grid;
  gap: 10px;
}

.tool-empty {
  padding: 16px;
  border-radius: 18px;
  border: 1px dashed var(--border-subtle);
  color: var(--text-secondary);
  background: rgba(255, 255, 255, 0.02);
}

@media (max-width: 1200px) {
  .pulse-hero,
  .overview-main-grid,
  .pulse-metrics,
  .metrics-grid {
    grid-template-columns: 1fr;
  }
}
</style>
