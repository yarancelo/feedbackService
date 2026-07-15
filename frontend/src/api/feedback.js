// Feedback endpoints.
import { request } from './client.js'

function buildQuery(params) {
  const query = new URLSearchParams()
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') query.append(key, value)
  })
  return query.toString()
}

export function createFeedback(topic, body) {
  return request('/feedbacks', { method: 'POST', body: { topic, body } })
}

export function listFeedbacks(params) {
  return request(`/feedbacks?${buildQuery(params)}`, { auth: true })
}

export function deleteFeedback(id) {
  return request(`/feedbacks/${id}`, { method: 'DELETE', auth: true })
}

export { buildQuery }
