import { describe, expect, it } from 'vitest'
import { clearToken, getToken, setToken } from '../../src/lib/token.js'

describe('token storage', () => {
  it('returns null when empty', () => {
    expect(getToken()).toBeNull()
  })

  it('sets and reads a token', () => {
    setToken('abc')
    expect(getToken()).toBe('abc')
  })

  it('clears a token', () => {
    setToken('abc')
    clearToken()
    expect(getToken()).toBeNull()
  })
})
