import { request } from './client.js'

export const listCategories = () => request('/categories')
export const listManagedCategories = () => request('/categories/manage', { auth: true })
export const createCategory = (body) => request('/categories', { method: 'POST', body, auth: true })
export const updateCategory = (id, body) => request(`/categories/${id}`, { method: 'PATCH', body, auth: true })
export const deleteCategory = (id) => request(`/categories/${id}`, { method: 'DELETE', auth: true })
