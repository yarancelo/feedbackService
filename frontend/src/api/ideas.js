import { request } from './client.js'

const BROWSER_KEY = 'improvement-wall-browser-key'

function query(params = {}) {
  const values = new URLSearchParams()
  Object.entries(params).forEach(([key, value]) => value != null && value !== '' && values.set(key, value))
  return values.toString()
}

export function browserKey() {
  let key = localStorage.getItem(BROWSER_KEY)
  if (!key) {
    key = globalThis.crypto?.randomUUID?.() ?? `browser-${Date.now()}-${Math.random().toString(16).slice(2)}`
    localStorage.setItem(BROWSER_KEY, key)
  }
  return key
}

export const createIdea = (body) => request('/ideas', { method: 'POST', body })
export const listIdeas = (params) => request(`/ideas?${query(params)}`, { auth: true })
export const updateIdeaStatus = (id, body) => request(`/ideas/${id}/status`, { method: 'PATCH', body, auth: true })
export const updateGoldStatus = (id, body) => request(`/ideas/${id}/gold`, { method: 'PATCH', body, auth: true })
export const confirmManualAuthor = (id) => request(`/ideas/${id}/confirm-author`, { method: 'POST', auth: true })
export const deleteIdea = (id) => request(`/ideas/${id}`, { method: 'DELETE', auth: true })
export const listWall = (page = 1) => request(`/wall?${query({ page, client_key: browserKey() })}`)
export const reactToIdea = (id, value) => request(`/ideas/${id}/reaction`, { method: 'POST', body: { client_key: browserKey(), value } })
export const leaderboard = (week) => request(`/leaderboard?${query({ week })}`, { auth: true })
export const leaderboardHistory = () => request('/leaderboard/history', { auth: true })
export const ideaBank = () => request(`/idea-bank?${query({ client_key: browserKey() })}`)
