<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'

import { apiGet } from '@/api/client'
import MetricTile from '@/components/MetricTile.vue'
import NewsCard from '@/components/NewsCard.vue'
import ProviderBadge from '@/components/ProviderBadge.vue'
import SectionPanel from '@/components/SectionPanel.vue'
import { useSystemStore } from '@/stores/system'
import type { MarketOverview } from '@/types'
import { compactNumber, formatCurrency, formatMarketPercent } from '@/utils/format'
import {
  buildLocalizedProviderBadgeLabel,
  buildLocalizedRuntimeSummary,
  getLocalizedHealthHeadline,
  translateStatus,
} from '@/utils/presentation'

const overview = ref<MarketOverview | null>(null)
const loading = ref(false)
const error = ref('')
const systemStore = useSystemStore()

async function loadOverview() {
  loading.value = true
  error.value = ''
  try {
    overview.value = await apiGet<MarketOverview>('/api/markets/overview')
  } catch (err) {
    error.value = err instanceof Error ? err.message : '加载市场总览失败。'
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

const runtimeSummary = computed(() =>
  systemStore.health ? buildLocalizedRuntimeSummary(systemStore.health) : '',
)

const runtimeHeadline = computed(() =>
  systemStore.health ? getLocalizedHealthHeadline(systemStore.health) : '',
)
</script>

<template>
  <div class="overview-layout">
    <section class="hero panel">
      <div>
        <div class="eyebrow">跨市场信号面板</div>
        <h2>在一个研究界面里同时跟踪美股、港股和 A 股。</h2>
        <p>先看数据源状态、重点标的、市场动量与新闻线索，再进入单股研究和策略实验。</p>
      </div>
      <div class="hero-badges" v-if="overview">
        <ProviderBadge :label="buildLocalizedProviderBadgeLabel(overview.provider, overview.source_status)" :status="overview.source_status" />
        <ProviderBadge
          v-if="systemStore.health"
          :label="buildLocalizedProviderBadgeLabel(systemStore.health.market_provider, systemStore.health.market_provider_status)"
          :status="systemStore.health.market_provider_status"
        />
        <ProviderBadge
          v-if="systemStore.health"
          :label="buildLocalizedProviderBadgeLabel(systemStore.health.news_provider, systemStore.health.news_provider_status)"
          :status="systemStore.health.news_provider_status"
        />
        <span class="mono generated-at">更新于 {{ new Date(overview.generated_at).toLocaleString() }}</span>
        <span v-if="systemStore.health" class="mono generated-at">{{ runtimeSummary }}</span>
        <p v-if="systemStore.health" class="runtime-note">{{ runtimeHeadline }}</p>
      </div>
    </section>

    <div v-if="loading" class="panel loading-block">正在加载市场总览...</div>
    <div v-else-if="error" class="panel loading-block error">{{ error }}</div>

    <template v-else-if="overview">
      <div class="market-grid">
        <SectionPanel
          v-for="section in overview.sections"
          :key="section.region"
          :title="section.title"
          :subtitle="`${section.region} 市场 / ${translateStatus(section.source_status)}`"
        >
          <template #actions>
            <ProviderBadge :label="translateStatus(section.source_status)" :status="section.source_status" />
          </template>
          <div class="metrics-grid">
            <MetricTile
              v-for="metric in section.metrics"
              :key="metric.symbol"
              :label="metric.label"
              :value="formatCurrency(metric.value)"
              :delta="formatMarketPercent(metric.change_percent)"
              :positive="metric.change_percent >= 0"
            />
          </div>
        </SectionPanel>
      </div>

      <div class="content-grid">
        <SectionPanel title="研究自选股" subtitle="当前重点跟踪标的">
          <div class="watchlist-grid">
            <RouterLink
              v-for="snapshot in overview.watchlist"
              :key="snapshot.symbol"
              class="watchlist-card panel"
              :to="`/stocks/${snapshot.symbol}`"
            >
              <div class="watchlist-top">
                <div class="eyebrow">{{ snapshot.symbol }}</div>
              <ProviderBadge :label="translateStatus(snapshot.source_status)" :status="snapshot.source_status" />
              </div>
              <h3>{{ snapshot.display_name }}</h3>
              <strong>{{ formatCurrency(snapshot.price) }}</strong>
              <div :class="snapshot.change_percent >= 0 ? 'status-positive' : 'status-negative'">
                {{ formatMarketPercent(snapshot.change_percent) }}
              </div>
              <p class="muted">成交量 {{ compactNumber(snapshot.volume) }} / 成交额 {{ compactNumber(snapshot.turnover) }}</p>
            </RouterLink>
          </div>
        </SectionPanel>

        <SectionPanel title="关联新闻" subtitle="与研究标的关联的最新线索">
          <div v-if="overview.top_news.length" class="news-grid">
            <NewsCard v-for="item in overview.top_news" :key="item.id" :item="item" />
          </div>
          <div v-else class="panel loading-block">当前暂无可归因新闻。</div>
        </SectionPanel>
      </div>
    </template>
  </div>
</template>

<style scoped>
.overview-layout {
  display: grid;
  gap: 24px;
}

.hero {
  display: grid;
  grid-template-columns: 1.2fr auto;
  gap: 24px;
  align-items: end;
  padding: 30px;
}

.hero h2 {
  max-width: 760px;
  margin: 10px 0 12px;
  font-size: clamp(2rem, 4vw, 3.3rem);
  line-height: 0.96;
  font-family: 'Chakra Petch', sans-serif;
}

.hero p {
  max-width: 720px;
  margin: 0;
  color: var(--text-secondary);
  line-height: 1.6;
}

.hero-badges {
  display: grid;
  justify-items: end;
  gap: 10px;
}

.generated-at {
  color: var(--text-muted);
}

.runtime-note {
  max-width: 320px;
  margin: 0;
  text-align: right;
  color: var(--text-secondary);
  line-height: 1.5;
}

.market-grid,
.content-grid {
  display: grid;
  gap: 20px;
}

.market-grid {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.content-grid {
  grid-template-columns: 0.95fr 1.05fr;
}

.metrics-grid,
.watchlist-grid,
.news-grid {
  display: grid;
  gap: 16px;
}

.watchlist-card {
  padding: 18px;
}

.watchlist-card h3,
.watchlist-card strong,
.watchlist-card p {
  margin: 0;
}

.watchlist-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.watchlist-card strong {
  font-size: 1.65rem;
  font-family: 'Chakra Petch', sans-serif;
}

.loading-block {
  padding: 22px;
}

.error {
  color: var(--negative);
}

@media (max-width: 1200px) {
  .market-grid,
  .content-grid,
  .hero {
    grid-template-columns: 1fr;
  }

  .hero-badges {
    justify-items: start;
  }

  .runtime-note {
    text-align: left;
  }
}
</style>
