import { request } from './client.js'
export const listManualAuthors = () => request('/manual-authors', { auth: true })
export const createManualAuthor = (body) => request('/manual-authors', { method: 'POST', body, auth: true })
export const updateManualAuthor = (id, body) => request(`/manual-authors/${id}`, { method: 'PATCH', body, auth: true })
export const deleteManualAuthor = (id) => request(`/manual-authors/${id}`, { method: 'DELETE', auth: true })
