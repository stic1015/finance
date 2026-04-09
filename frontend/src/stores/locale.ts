import { defineStore } from 'pinia'

import { type Locale, createTranslator } from '@/i18n'

const STORAGE_KEY = 'finance-locale'

function detectInitialLocale(): Locale {
  const stored = window.localStorage.getItem(STORAGE_KEY)
  if (stored === 'zh-CN' || stored === 'en-US') return stored
  return 'zh-CN'
}

export const useLocaleStore = defineStore('locale', {
  state: () => ({
    locale: detectInitialLocale() as Locale,
  }),
  getters: {
    t(state) {
      return createTranslator(state.locale)
    },
  },
  actions: {
    setLocale(next: Locale) {
      this.locale = next
      window.localStorage.setItem(STORAGE_KEY, next)
    },
    toggleLocale() {
      this.setLocale(this.locale === 'zh-CN' ? 'en-US' : 'zh-CN')
    },
  },
})
