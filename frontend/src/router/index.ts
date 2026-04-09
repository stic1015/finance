import { createRouter, createWebHistory } from 'vue-router'

import MarketOverviewView from '@/views/OpportunityDiscoveryView.vue'
import StockResearchView from '@/views/StockResearchDeskView.vue'
import StrategyLabView from '@/views/StrategyLabWorkbenchView.vue'

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'overview', component: MarketOverviewView },
    { path: '/stocks/:symbol', name: 'stock', component: StockResearchView, props: true },
    { path: '/strategy-lab', name: 'strategy-lab', component: StrategyLabView },
  ],
})
