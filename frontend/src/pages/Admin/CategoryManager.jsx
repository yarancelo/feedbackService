import { useEffect, useState } from 'react'
import Button from '../../components/Button.jsx'
import ErrorBanner from '../../components/ErrorBanner.jsx'
import { createCategory, deleteCategory, listManagedCategories, updateCategory } from '../../api/categories.js'

export default function CategoryManager() {
  const [categories, setCategories] = useState([])
  const [name, setName] = useState('')
  const [error, setError] = useState('')
  async function load() { try { setCategories(await listManagedCategories()) } catch (requestError) { setError(requestError.message) } }
  useEffect(() => { load() }, [])
  async function add(event) { event.preventDefault(); if (!name.trim()) return; try { await createCategory({ name: name.trim() }); setName(''); load() } catch (requestError) { setError(requestError.message) } }
  async function toggle(category) { try { await updateCategory(category.id, { is_active: !category.is_active }); load() } catch (requestError) { setError(requestError.message) } }
  async function remove(category) { if (!window.confirm(`Удалить тему «${category.name}»? Уже отправленные идеи останутся без изменений.`)) return; try { await deleteCategory(category.id); load() } catch (requestError) { setError(requestError.message) } }
  return <section className="category-manager"><div><p className="eyebrow">Настройки формы</p><h2>Темы идей</h2><p>Эти пункты видит сотрудник в выпадающем списке «Тема».</p></div><ErrorBanner message={error} /><form className="category-manager__add" onSubmit={add}><input className="input" value={name} onChange={(event) => setName(event.target.value)} placeholder="Например: Безопасность" maxLength="100" /><Button type="submit">Добавить</Button></form><div className="category-manager__list">{categories.map((category) => <div className="category-manager__row" key={category.id}><span>{category.name}</span><div><Button type="button" variant="ghost" onClick={() => toggle(category)}>{category.is_active ? 'Скрыть' : 'Показать'}</Button><Button type="button" variant="danger" onClick={() => remove(category)}>Удалить</Button></div></div>)}</div></section>
}
