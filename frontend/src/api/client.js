// Low-level REST client. Small, single-purpose helpers + one request().
import { logger } from '../lib/logger.js'
import { getToken } from '../lib/token.js'

const BASE = '/api'

export class ApiError extends Error {
  constructor(message, status) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

function buildHeaders(auth) {
  const headers = { 'Content-Type': 'application/json' }
  if (auth) {
    const token = getToken()
    if (token) headers['Authorization'] = `Bearer ${token}`
  }
  return headers
}

function extractErrorMessage(data) {
  const detail = data && data.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) return detail.map((d) => d.msg).join(', ')
  return 'Не получилось выполнить действие. Попробуйте ещё раз.'
}

async function parseBody(response) {
  if (response.status === 204) return null
  try {
    return await response.json()
  } catch {
    return null
  }
}

export async function request(path, { method = 'GET', body, auth = false } = {}) {
  logger.debug('API request', method, path)
  const response = await fetch(`${BASE}${path}`, {
    method,
    headers: buildHeaders(auth),
    body: body ? JSON.stringify(body) : undefined,
  })

  const data = await parseBody(response)

  if (!response.ok) {
    const message = extractErrorMessage(data)
    logger.error('API error', method, path, response.status, message)
    throw new ApiError(message, response.status)
  }

  logger.debug('API ok', method, path, response.status)
  return data
}
