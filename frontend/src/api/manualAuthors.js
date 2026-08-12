import { request } from './client.js'
export const listManualAuthors = () => request('/manual-authors', { auth: true })
export const confirmManualAuthor = (ideaId) => request(`/manual-authors/from-idea/${ideaId}`, { method: 'POST', auth: true })
export const updateManualAuthor = (id, body) => request(`/manual-authors/${id}`, { method: 'PATCH', body, auth: true })
