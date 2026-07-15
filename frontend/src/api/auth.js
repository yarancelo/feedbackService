// Auth endpoints.
import { request } from './client.js'

export function login(login, password) {
  return request('/auth/login', { method: 'POST', body: { login, password } })
}
