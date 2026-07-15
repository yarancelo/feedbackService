// Feedback list state: pagination, date filters, sorting, load + delete.
import { useCallback, useEffect, useState } from 'react'
import { deleteFeedback, listFeedbacks } from '../api/feedback.js'
import { logger } from '../lib/logger.js'

function toBounds(dateFrom, dateTo) {
  const bounds = {}
  if (dateFrom) bounds.date_from = `${dateFrom}T00:00:00`
  if (dateTo) bounds.date_to = `${dateTo}T23:59:59`
  return bounds
}

export function useFeedbackList({ onUnauthorized }) {
  const [items, setItems] = useState([])
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(0)
  const [total, setTotal] = useState(0)
  const [order, setOrder] = useState('desc')
  const [dateFrom, setDateFrom] = useState('')
  const [dateTo, setDateTo] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const load = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      const data = await listFeedbacks({ page, order, ...toBounds(dateFrom, dateTo) })
      setItems(data.items)
      setTotal(data.total)
      setTotalPages(data.total_pages)
      logger.debug('Loaded feedback page', page, 'of', data.total_pages)
    } catch (err) {
      if (err.status === 401) {
        logger.warn('Session expired while listing feedback')
        onUnauthorized()
        return
      }
      logger.error('Failed to load feedback', err.message)
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [page, order, dateFrom, dateTo, onUnauthorized])

  useEffect(() => {
    load()
  }, [load])

  const remove = useCallback(
    async (id) => {
      try {
        await deleteFeedback(id)
        logger.info('Deleted feedback', id)
        if (items.length === 1 && page > 1) setPage((p) => p - 1)
        else load()
      } catch (err) {
        if (err.status === 401) onUnauthorized()
        else setError(err.message)
      }
    },
    [items.length, page, load, onUnauthorized],
  )

  const applyFilters = useCallback(() => {
    setPage(1)
    load()
  }, [load])

  return {
    items, page, totalPages, total, order, dateFrom, dateTo, loading, error,
    setOrder, setDateFrom, setDateTo, setPage,
    load, remove, applyFilters,
  }
}
