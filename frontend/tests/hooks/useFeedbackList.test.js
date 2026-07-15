import { act, renderHook, waitFor } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import * as feedbackApi from '../../src/api/feedback.js'
import { useFeedbackList } from '../../src/hooks/useFeedbackList.js'

afterEach(() => vi.restoreAllMocks())

function page(items, extra = {}) {
  return { items, total: items.length, total_pages: 1, ...extra }
}

// A stable onUnauthorized reference is required: passing a fresh function each
// render would invalidate the hook's useCallback/useEffect on every render.
function render(onUnauthorized = vi.fn()) {
  return renderHook(() => useFeedbackList({ onUnauthorized }))
}

const SAMPLE = { id: '1', topic: 't', body: 'b', created_at: '2026-01-01T00:00:00Z' }

describe('useFeedbackList', () => {
  it('loads items on mount', async () => {
    vi.spyOn(feedbackApi, 'listFeedbacks').mockResolvedValue(page([SAMPLE]))
    const { result } = render()
    await waitFor(() => expect(result.current.loading).toBe(false))
    expect(result.current.items).toHaveLength(1)
    expect(result.current.total).toBe(1)
  })

  it('calls onUnauthorized on 401', async () => {
    vi.spyOn(feedbackApi, 'listFeedbacks').mockRejectedValue({ status: 401 })
    const onUnauthorized = vi.fn()
    render(onUnauthorized)
    await waitFor(() => expect(onUnauthorized).toHaveBeenCalled())
  })

  it('surfaces non-401 errors', async () => {
    vi.spyOn(feedbackApi, 'listFeedbacks').mockRejectedValue({ status: 500, message: 'сбой' })
    const { result } = render()
    await waitFor(() => expect(result.current.error).toBe('сбой'))
  })

  it('remove deletes then reloads', async () => {
    vi.spyOn(feedbackApi, 'listFeedbacks').mockResolvedValue(page([SAMPLE]))
    const del = vi.spyOn(feedbackApi, 'deleteFeedback').mockResolvedValue(null)
    const { result } = render()
    await waitFor(() => expect(result.current.loading).toBe(false))

    await act(async () => {
      await result.current.remove('1')
    })
    expect(del).toHaveBeenCalledWith('1')
  })
})
