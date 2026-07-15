import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { ApiError, request } from '../../src/api/client.js'
import { setToken } from '../../src/lib/token.js'

function mockResponse({ ok = true, status = 200, body = {} }) {
  return { ok, status, json: async () => body }
}

beforeEach(() => {
  global.fetch = vi.fn()
})
afterEach(() => {
  vi.restoreAllMocks()
})

describe('request', () => {
  it('returns parsed body on success', async () => {
    global.fetch.mockResolvedValue(mockResponse({ body: { a: 1 } }))
    await expect(request('/x')).resolves.toEqual({ a: 1 })
  })

  it('returns null on 204', async () => {
    global.fetch.mockResolvedValue(mockResponse({ status: 204 }))
    await expect(request('/x', { method: 'DELETE' })).resolves.toBeNull()
  })

  it('throws ApiError with status on failure', async () => {
    global.fetch.mockResolvedValue(mockResponse({ ok: false, status: 404, body: { detail: 'нет' } }))
    await expect(request('/x')).rejects.toMatchObject({ status: 404, message: 'нет' })
    await expect(request('/x')).rejects.toBeInstanceOf(ApiError)
  })

  it('flattens pydantic validation error arrays', async () => {
    global.fetch.mockResolvedValue(
      mockResponse({ ok: false, status: 422, body: { detail: [{ msg: 'a' }, { msg: 'b' }] } }),
    )
    await expect(request('/x')).rejects.toMatchObject({ message: 'a, b' })
  })

  it('adds Authorization header when auth requested and token present', async () => {
    setToken('tok-123')
    global.fetch.mockResolvedValue(mockResponse({ body: {} }))
    await request('/x', { auth: true })
    const headers = global.fetch.mock.calls[0][1].headers
    expect(headers.Authorization).toBe('Bearer tok-123')
  })

  it('omits Authorization header without auth', async () => {
    setToken('tok-123')
    global.fetch.mockResolvedValue(mockResponse({ body: {} }))
    await request('/x')
    const headers = global.fetch.mock.calls[0][1].headers
    expect(headers.Authorization).toBeUndefined()
  })
})
