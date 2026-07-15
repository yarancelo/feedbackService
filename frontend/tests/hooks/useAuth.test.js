import { act, renderHook } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import * as authApi from '../../src/api/auth.js'
import { useAuth } from '../../src/hooks/useAuth.js'
import { getToken, setToken } from '../../src/lib/token.js'

afterEach(() => vi.restoreAllMocks())

describe('useAuth', () => {
  it('starts unauthenticated when no token', () => {
    const { result } = renderHook(() => useAuth())
    expect(result.current.authed).toBe(false)
  })

  it('login stores the token and flips authed', async () => {
    vi.spyOn(authApi, 'login').mockResolvedValue({ access_token: 'tok' })
    const { result } = renderHook(() => useAuth())
    await act(async () => {
      await result.current.login('admin', 'password')
    })
    expect(result.current.authed).toBe(true)
    expect(getToken()).toBe('tok')
  })

  it('logout clears the token', () => {
    setToken('tok')
    const { result } = renderHook(() => useAuth())
    expect(result.current.authed).toBe(true)
    act(() => result.current.logout())
    expect(result.current.authed).toBe(false)
    expect(getToken()).toBeNull()
  })
})
