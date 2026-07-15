import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { login } from '../../src/api/auth.js'

beforeEach(() => {
  global.fetch = vi.fn().mockResolvedValue({ ok: true, status: 200, json: async () => ({ access_token: 't' }) })
})
afterEach(() => vi.restoreAllMocks())

describe('login', () => {
  it('POSTs credentials to /api/auth/login', async () => {
    await login('admin', 'password')
    const [url, options] = global.fetch.mock.calls[0]
    expect(url).toBe('/api/auth/login')
    expect(options.method).toBe('POST')
    expect(JSON.parse(options.body)).toEqual({ login: 'admin', password: 'password' })
  })
})
