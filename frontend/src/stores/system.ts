import { defineStore } from 'pinia'

import { apiGet } from '@/api/client'
import type { HealthResponse } from '@/types'

export const useSystemStore = defineStore('system', {
  state: () => ({
    health: null as HealthResponse | null,
    loading: false,
    error: '',
  }),
  actions: {
    async loadHealth() {
      this.loading = true
      this.error = ''
      try {
        this.health = await apiGet<HealthResponse>('/api/system/health')
      } catch (error) {
        this.error = error instanceof Error ? error.message : 'Failed to load system health.'
      } finally {
        this.loading = false
      }
    },
  },
})
