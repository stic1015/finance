import { readFileSync } from 'node:fs'
import { describe, expect, it } from 'vitest'

const componentPath = 'D:/Codex/Finance/frontend/src/components/ResearchStrategyFormClean.vue'

describe('ResearchStrategyFormClean interval wiring', () => {
  it('keeps 30m as default and sends interval in submit payload', () => {
    const source = readFileSync(componentPath, 'utf-8')
    expect(source).toContain("interval: '30m'")
    expect(source).toContain("interval: form.interval")
    expect(source).toContain('<option value="30m">30m</option>')
  })
})
