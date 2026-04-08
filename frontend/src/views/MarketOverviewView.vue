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
import { buildProviderBadgeLabel, buildRuntimeSummary, getHealthHeadline } from '@/utils/runtime'

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
    error.value = err instanceof Error ? err.message : 'Failed to load market overview.'
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
  systemStore.health ? buildRuntimeSummary(systemStore.health) : '',
)

const runtimeHeadline = computed(() =>
  systemStore.health ? getHealthHeadline(systemStore.health) : '',
)
</script>

<template>
  <div class="overview-layout">
    <section class="hero panel">
      <div>
        <div class="eyebrow">Cross-Market Signal Board</div>
        <h2>Watch US, Hong Kong, and A-share moves through one research surface.</h2>
        <p>
          Track provider state, hot symbols, market momentum, and signal-linked news before diving into single-stock
          analysis.
        </p>
      </div>
      <div class="hero-badges" v-if="overview">
        <ProviderBadge :label="overview.provider" :status="overview.source_status" />
        <ProviderBadge
          v-if="systemStore.health"
          :label="buildProviderBadgeLabel(systemStore.health.market_provider, systemStore.health.market_provider_status)"
          :status="systemStore.health.market_provider_status"
        />
        <ProviderBadge
          v-if="systemStore.health"
          :label="buildProviderBadgeLabel(systemStore.health.news_provider, systemStore.health.news_provider_status)"
          :status="systemStore.health.news_provider_status"
        />
        <span class="mono generated-at">Updated {{ new Date(overview.generated_at).toLocaleString() }}</span>
        <span v-if="systemStore.health" class="mono generated-at">{{ runtimeSummary }}</span>
        <p v-if="systemStore.health" class="runtime-note">{{ runtimeHeadline }}</p>
      </div>
    </section>

    <div v-if="loading" class="panel loading-block">Loading market overview...</div>
    <div v-else-if="error" class="panel loading-block error">{{ error }}</div>

    <template v-else-if="overview">
      <div class="market-grid">
        <SectionPanel
          v-for="section in overview.sections"
          :key="section.region"
          :title="section.title"
          :subtitle="`${section.region} Region`"
        >
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
        <SectionPanel title="Research Watchlist" subtitle="Tracked symbols">
          <div class="watchlist-grid">
            <RouterLink
              v-for="snapshot in overview.watchlist"
              :key="snapshot.symbol"
              class="watchlist-card panel"
              :to="`/stocks/${snapshot.symbol}`"
            >
              <div class="eyebrow">{{ snapshot.symbol }}</div>
              <h3>{{ snapshot.display_name }}</h3>
              <strong>{{ formatCurrency(snapshot.price) }}</strong>
              <div :class="snapshot.change_percent >= 0 ? 'status-positive' : 'status-negative'">
                {{ formatMarketPercent(snapshot.change_percent) }}
              </div>
              <p class="muted">
                Vol {{ compactNumber(snapshot.volume) }} · Turnover {{ compactNumber(snapshot.turnover) }}
              </p>
            </RouterLink>
          </div>
        </SectionPanel>

        <SectionPanel title="Latest Related News" subtitle="Signal-linked headlines">
          <div class="news-grid">
            <NewsCard v-for="item in overview.top_news" :key="item.id" :item="item" />
          </div>
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
