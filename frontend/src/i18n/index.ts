import { enUS } from './messages/en-US-fixed'
import { zhCN } from './messages/zh-CN'

export type Locale = 'zh-CN' | 'en-US'

export const messages = {
  'zh-CN': zhCN,
  'en-US': enUS,
} as const

function resolvePath(obj: Record<string, unknown>, path: string): unknown {
  return path.split('.').reduce<unknown>((acc, key) => {
    if (acc && typeof acc === 'object' && key in (acc as Record<string, unknown>)) {
      return (acc as Record<string, unknown>)[key]
    }
    return undefined
  }, obj)
}

export function createTranslator(locale: Locale) {
  return (path: string, fallback?: string) => {
    const value = resolvePath(messages[locale] as unknown as Record<string, unknown>, path)
    if (typeof value === 'string') return value
    return fallback ?? path
  }
}
