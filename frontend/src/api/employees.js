import { request } from './client.js'
export const listEmployees = () => request('/employees')
