import { describe, expect, it } from 'vitest'

import { compactNumber, formatPercent } from '../src/utils/format'
import { normalizeDisplaySymbol } from '../src/utils/symbol'

describe('format helpers', () => {
  it('formats decimal returns as percentages', () => {
    expect(formatPercent(0.1234)).toBe('+12.34%')
  })

  it('normalizes symbol display tokens', () => {
    expect(normalizeDisplaySymbol('00700/hk')).toBe('00700.HK')
  })

  it('compacts large numbers', () => {
    expect(compactNumber(1200000)).toContain('1.2')
  })
})
