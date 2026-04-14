import { describe, expect, it } from 'vitest'

import { FALLBACK_STRATEGIES, getStrategyFields, localizeStrategyDefinition } from '../src/constants/strategies'

describe('strategy localization mapping', () => {
  it('maps strategy metadata by strategy.name for zh-CN', () => {
    const base = FALLBACK_STRATEGIES.find((item) => item.name === 'sar_ema144_breakout')
    if (!base) throw new Error('Missing fallback strategy for sar_ema144_breakout')
    const localized = localizeStrategyDefinition(base, 'zh-CN')
    expect(localized.label).toContain('SAR')
    expect(localized.description).toContain('EMA144')
  })

  it('returns localized strategy fields by locale', () => {
    const zhFields = getStrategyFields('sar_ema144_breakout', 'zh-CN')
    const enFields = getStrategyFields('sar_ema144_breakout', 'en-US')
    expect(zhFields[0].label).toContain('EMA')
    expect(enFields[0].label).toContain('EMA')
    expect(enFields.some((item) => item.key === 'sar_step')).toBe(true)
  })
})
