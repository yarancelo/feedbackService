import { afterEach, describe, expect, it, vi } from 'vitest'
import { logger, setLevel } from '../../src/lib/logger.js'

afterEach(() => {
  setLevel('debug')
  vi.restoreAllMocks()
})

describe('logger', () => {
  it('emits at or above the threshold', () => {
    const spy = vi.spyOn(console, 'warn').mockImplementation(() => {})
    setLevel('warn')
    logger.warn('hi')
    expect(spy).toHaveBeenCalledWith('[WARN]', 'hi')
  })

  it('suppresses below the threshold', () => {
    const spy = vi.spyOn(console, 'debug').mockImplementation(() => {})
    setLevel('error')
    logger.debug('quiet')
    expect(spy).not.toHaveBeenCalled()
  })

  it('routes error to console.error', () => {
    const spy = vi.spyOn(console, 'error').mockImplementation(() => {})
    logger.error('boom')
    expect(spy).toHaveBeenCalled()
  })
})
