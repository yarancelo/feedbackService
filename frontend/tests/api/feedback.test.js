import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { buildQuery, createFeedback, deleteFeedback, listFeedbacks } from '../../src/api/feedback.js'

beforeEach(() => {
  global.fetch = vi.fn().mockResolvedValue({ ok: true, status: 200, json: async () => ({}) })
})
afterEach(() => vi.restoreAllMocks())

describe('buildQuery', () => {
  it('drops empty values', () => {
    expect(buildQuery({ page: 1, order: 'desc', date_from: '', date_to: null })).toBe('page=1&order=desc')
  })
})

describe('feedback endpoints', () => {
  it('createFeedback POSTs topic and body', async () => {
    await createFeedback('t', 'b')
    const [url, options] = global.fetch.mock.calls[0]
    expect(url).toBe('/api/feedbacks')
    expect(JSON.parse(options.body)).toEqual({ topic: 't', body: 'b' })
  })

  it('listFeedbacks builds a query string', async () => {
    await listFeedbacks({ page: 2, order: 'asc' })
    expect(global.fetch.mock.calls[0][0]).toBe('/api/feedbacks?page=2&order=asc')
  })

  it('deleteFeedback issues a DELETE', async () => {
    await deleteFeedback('id-1')
    const [url, options] = global.fetch.mock.calls[0]
    expect(url).toBe('/api/feedbacks/id-1')
    expect(options.method).toBe('DELETE')
  })
})
