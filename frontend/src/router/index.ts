import { createRouter, createWebHistory } from 'vue-router'

import MarketOverviewView from '@/views/MarketOverviewView.vue'
import StockResearchView from '@/views/StockResearchView.vue'
import StrategyLabView from '@/views/StrategyLabView.vue'

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'overview', component: MarketOverviewView },
    { path: '/stocks/:symbol', name: 'stock', component: StockResearchView, props: true },
    { path: '/strategy-lab', name: 'strategy-lab', component: StrategyLabView },
  ],
})
