import { defineStore } from 'pinia'

export type WatchGroup = {
  id: string
  name: string
  symbols: string[]
}

export type AlertRule = {
  id: string
  symbol: string
  type: 'price_move' | 'news_ready' | 'forecast_shift'
  enabled: boolean
}

export type AlertEvent = {
  id: string
  symbol: string
  type: AlertRule['type']
  status: 'hit' | 'idle'
  title: string
  read: boolean
  created_at: string
}

const STORAGE_KEY = 'finance-watch-state'

function loadState() {
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY)
    if (!raw) {
      return {
        groups: [{ id: 'default', name: 'default', symbols: ['HK.00700', 'SH.600519'] }],
        rules: [],
        events: [],
      }
    }
    return JSON.parse(raw)
  } catch {
    return {
      groups: [{ id: 'default', name: 'default', symbols: ['HK.00700', 'SH.600519'] }],
      rules: [],
      events: [],
    }
  }
}

export const useWatchStore = defineStore('watch', {
  state: () => loadState() as { groups: WatchGroup[]; rules: AlertRule[]; events: AlertEvent[] },
  actions: {
    persist() {
      window.localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify({ groups: this.groups, rules: this.rules, events: this.events }),
      )
    },
    addSymbol(symbol: string, groupId = 'default') {
      const group = this.groups.find((item) => item.id === groupId)
      if (!group) return
      if (!group.symbols.includes(symbol)) group.symbols.push(symbol)
      this.persist()
    },
    addRule(rule: AlertRule) {
      this.rules.unshift(rule)
      this.persist()
    },
    addEvent(event: AlertEvent) {
      const exists = this.events.find((item) => item.id === event.id)
      if (!exists) {
        this.events.unshift(event)
        this.persist()
      }
    },
    markRead(id: string) {
      const event = this.events.find((item) => item.id === id)
      if (!event) return
      event.read = true
      this.persist()
    },
  },
})
