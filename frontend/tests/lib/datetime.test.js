import { describe, expect, it } from 'vitest'
import { formatTimestamp } from '../../src/lib/datetime.js'

describe('formatTimestamp', () => {
  it('formats an ISO string to a non-empty localized string', () => {
    const result = formatTimestamp('2026-01-15T09:30:00Z')
    expect(typeof result).toBe('string')
    expect(result).toContain('2026')
  })
})
