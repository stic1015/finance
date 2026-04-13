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
const strongestRegion = computed(() =>
  [...sectorStrength.value].sort((a, b) => Math.abs(b.avg_change) - Math.abs(a.avg_change))[0] ?? null,
)
const actionBoard = computed(() =>
  [...filteredWatchlist.value]
    .sort((a, b) => Math.abs(b.change_percent) - Math.abs(a.change_percent))
    .slice(0, 6)
    .map((item) => {
      const relatedBrief = briefItems.value.find((news) =>
        news.matched_symbols.some((match) => item.symbol.startsWith(`${match}.`) || item.symbol.startsWith(match)),
      )
      return {
        ...item,
        note: relatedBrief
          ? relatedBrief.title
          : item.source_status === 'live'
            ? localeStore.locale === 'zh-CN'
              ? '实时行情可直接进入研究页确认。'
              : 'Live quote available for immediate research follow-up.'
            : localeStore.locale === 'zh-CN'
              ? '优先核对数据状态，再决定是否加入观察。'
              : 'Validate feed status before adding it to your watch flow.',
      }
    }),
)
const watchGroupPreview = computed(() => watchStore.groups.slice(0, 4))

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
  {
    label: localeStore.locale === 'zh-CN' ? '主导市场' : 'Leading Region',
    value: strongestRegion.value?.region ?? '-',
    delta: strongestRegion.value ? formatMarketPercent(strongestRegion.value.avg_change) : undefined,
    positive: strongestRegion.value ? strongestRegion.value.avg_change >= 0 : null,
  },
])
</script>

<template>
  <div class="overview-layout">
    <section v-if="overview" class="pulse-hero panel">
      <div class="pulse-copy">
        <div class="eyebrow">{{ localeStore.t('overview.eyebrow') }}</div>
        <h2>{{ localeStore.t('overview.opportunityBoard') }}</h2>
        <p>{{ localeStore.t('overview.description') }}</p>
        <div class="pulse-meta">
          <ProviderBadge
            :label="buildLocalizedProviderBadgeLabel(overview.provider, overview.source_status)"
            :status="overview.source_status"
          />
          <span class="mono">
            {{ localeStore.t('overview.updatedAt') }} {{ new Date(overview.generated_at).toLocaleString() }}
          </span>
          <span class="mono">{{ runtimeSummary }}</span>
        </div>
      </div>
      <div class="pulse-metrics">
        <MetricTile v-for="tile in summaryTiles" :key="tile.label" :label="tile.label" :value="tile.value" />
      </div>
    </section>

    <div v-if="loadingOverview" class="panel empty-shell">{{ localeStore.t('common.loading') }}</div>
    <div v-else-if="overviewError" class="panel empty-shell error">{{ overviewError }}</div>

    <template v-else-if="overview">
      <div class="overview-main-grid">
        <div class="main-column">
          <SectionPanel :title="localeStore.t('overview.opportunityBoard')" :subtitle="localeStore.t('common.discoverOpportunities')">
            <template #actions>
              <div class="filter-group">
                <button type="button" class="interactive-chip" :class="{ active: filter === 'all' }" @click="filter = 'all'">{{ localeStore.t('common.all') }}</button>
                <button type="button" class="interactive-chip" :class="{ active: filter === 'live' }" @click="filter = 'live'">{{ localeStore.t('overview.onlyRealtime') }}</button>
                <button type="button" class="interactive-chip" :class="{ active: filter === 'news' }" @click="filter = 'news'">{{ localeStore.t('overview.onlyWithNews') }}</button>
                <button type="button" class="interactive-chip" :class="{ active: filter === 'backtest' }" @click="filter = 'backtest'">{{ localeStore.t('overview.onlyBacktestReady') }}</button>
              </div>
            </template>

            <div class="board-shell">
              <div class="pulse-strip">
                <article v-for="sector in sectorStrength" :key="sector.region" class="sector-card glass-line">
                  <div class="sector-top">
                    <div>
                      <div class="eyebrow">{{ sector.region }}</div>
                      <strong>{{ sector.title }}</strong>
                    </div>
                    <ProviderBadge :label="translateStatus(sector.source_status)" :status="sector.source_status" />
                  </div>
                  <div :class="sector.avg_change >= 0 ? 'status-positive sector-value' : 'status-negative sector-value'">
                    {{ formatMarketPercent(sector.avg_change) }}
                  </div>
                </article>
              </div>

              <div class="board-layout">
                <div class="board-main">
                  <div class="board-intro glass-line">
                    <div>
                      <div class="eyebrow">{{ localeStore.locale === 'zh-CN' ? '主判断' : 'Primary Read' }}</div>
                      <strong>{{ strongestRegion ? strongestRegion.title : (localeStore.locale === 'zh-CN' ? '等待市场脉冲数据' : 'Waiting for market pulse') }}</strong><!--
                        {{
                          strongestRegion
                            ? `${strongestRegion.title} ${localeStore.locale === 'zh-CN' ? '正在主导今日节奏' : 'is setting today\\'s tone'}`
                            : localeStore.locale === 'zh-CN'
                              ? '等待市场脉冲数据'
                              : 'Waiting for market pulse'
                        }}
                      -->
                    </div>
                    <p>
                      {{
                        localeStore.locale === 'zh-CN'
                          ? '先从主榜单锁定候选，再用右侧动作区和快讯确认是否进入研究、观察或预警。'
                          : 'Use the board to lock candidates first, then validate the next move with actions and briefs.'
                      }}
                    </p>
                  </div>
                  <RankedSymbolTableClean :items="hotList" />
                </div>

                <aside class="action-rail">
                  <article v-for="item in actionBoard" :key="item.symbol" class="action-card panel">
                    <div class="action-head">
                      <div>
                        <div class="eyebrow">{{ item.symbol }}</div>
                        <strong>{{ item.display_name }}</strong>
                      </div>
                      <span :class="item.change_percent >= 0 ? 'status-positive' : 'status-negative'">
                        {{ formatMarketPercent(item.change_percent) }}
                      </span>
                    </div>
                    <p>{{ item.note }}</p>
                    <RouterLink class="action-link" :to="`/stocks/${item.symbol}`">
                      {{ localeStore.locale === 'zh-CN' ? '进入研究页' : 'Open Research' }}
                    </RouterLink>
                  </article>
                </aside>
              </div>
            </div>
          </SectionPanel>

          <SectionPanel
            :title="localeStore.locale === 'zh-CN' ? '次级读数' : 'Secondary Read'"
            :subtitle="localeStore.locale === 'zh-CN' ? '用来确认节奏，不与主榜单抢注意力' : 'Confirmation layer, not a competing main board'"
          >
            <div class="secondary-grid">
              <article v-for="item in movers.slice(0, 6)" :key="item.symbol" class="secondary-card glass-line">
                <div class="secondary-row">
                  <div>
                    <div class="eyebrow">{{ item.symbol }}</div>
                    <strong>{{ item.display_name }}</strong>
                  </div>
                  <span :class="item.change_percent >= 0 ? 'status-positive' : 'status-negative'">
                    {{ formatMarketPercent(item.change_percent) }}
                  </span>
                </div>
                <span class="mono">{{ localeStore.t('common.volume') }} {{ item.volume }}</span>
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

          <SectionPanel :title="localeStore.t('overview.currentWatchlist')" :subtitle="localeStore.t('overview.watchGroups')">
            <div v-if="watchGroupPreview.length" class="watchlist-grid">
              <article v-for="group in watchGroupPreview" :key="group.id" class="watch-card glass-line">
                <div class="eyebrow">{{ group.name }}</div>
                <strong>{{ group.symbols.length }}</strong>
                <p class="muted">{{ group.symbols.join(' / ') }}</p>
              </article>
            </div>
            <div v-else class="tool-empty">
              {{ localeStore.locale === 'zh-CN' ? '还没有分组观察池，先从主榜单挑选候选。' : 'No watch groups yet. Start by selecting candidates from the board.' }}
            </div>
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
.watchlist-grid,
.pulse-strip,
.secondary-grid {
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

.board-shell,
.board-main,
.action-rail {
  display: grid;
  gap: 18px;
}

.pulse-strip {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.sector-card,
.secondary-card,
.watch-card,
.board-intro {
  padding: 16px;
}

.sector-top,
.secondary-row,
.action-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.sector-card strong,
.secondary-card strong,
.watch-card strong,
.board-intro strong,
.action-card strong {
  font-family: 'Chakra Petch', sans-serif;
}

.sector-value {
  font-size: 1.7rem;
  font-family: 'Chakra Petch', sans-serif;
}

.board-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 280px;
  gap: 18px;
}

.board-intro {
  display: grid;
  gap: 10px;
}

.board-intro p,
.action-card p {
  margin: 0;
  color: var(--text-secondary);
  line-height: 1.55;
}

.action-card {
  padding: 18px;
  display: grid;
  gap: 14px;
}

.action-link {
  display: inline-flex;
  align-items: center;
  width: fit-content;
  min-height: 38px;
  padding: 8px 14px;
  border-radius: 999px;
  border: 1px solid var(--border-subtle);
  color: var(--accent);
  background: var(--accent-soft);
}

.metrics-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.secondary-grid {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.secondary-card {
  display: grid;
  gap: 14px;
}

.secondary-card span {
  color: var(--text-muted);
  font-size: 0.76rem;
}

.filter-group {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.watch-card {
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
  .board-layout,
  .secondary-grid,
  .pulse-metrics,
  .metrics-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 860px) {
  .pulse-strip {
    grid-template-columns: 1fr;
  }
}
</style>
