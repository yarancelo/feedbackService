import { request } from './client.js'
import { browserKey } from './ideas.js'

export const listComments = (ideaId) => request(`/ideas/${ideaId}/comments`)
export const createComment = (ideaId, body) => request(`/ideas/${ideaId}/comments`, { method: 'POST', body: { client_key: browserKey(), body } })
