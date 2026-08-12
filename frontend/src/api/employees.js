import { request } from './client.js'
export const searchEmployees = (query) => query.trim().length < 3 ? Promise.resolve([]) : request(`/employees/search?q=${encodeURIComponent(query.trim())}`)
