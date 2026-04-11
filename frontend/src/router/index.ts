import { createRouter, createWebHistory } from 'vue-router'

import MarketOverviewView from '@/views/OpportunityDiscoveryTerminalView.vue'
import StockResearchView from '@/views/StockResearchDeskCleanView.vue'
import StrategyLabView from '@/views/StrategyLabWorkbenchTerminalView.vue'

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'overview', component: MarketOverviewView },
    { path: '/stocks/:symbol', name: 'stock', component: StockResearchView, props: true },
    { path: '/strategy-lab', name: 'strategy-lab', component: StrategyLabView },
  ],
})
