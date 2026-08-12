import { useEffect, useState } from 'react'
import Button from '../../components/Button.jsx'
import ErrorBanner from '../../components/ErrorBanner.jsx'
import { listManualAuthors, updateManualAuthor } from '../../api/manualAuthors.js'

export default function ManualAuthorManager() {
  const [authors, setAuthors] = useState([]); const [error, setError] = useState('')
  async function load() { try { setAuthors(await listManualAuthors()) } catch (requestError) { setError(requestError.message) } }
  useEffect(() => { load() }, [])
  async function edit(author) { const fullName = window.prompt('ФИО', author.full_name); if (!fullName?.trim()) return; const department = window.prompt('Отдел', author.department || '') ?? author.department; const company = window.prompt('Компания', author.company || '') ?? author.company; const position = window.prompt('Должность', author.position || '') ?? author.position; try { await updateManualAuthor(author.id, { full_name: fullName.trim(), department, company, position }); load() } catch (requestError) { setError(requestError.message) } }
  return <section className="manual-authors"><h2>Подтверждённые авторы</h2><p>Сотрудники, добавленные вручную и отсутствующие в справочнике Bitrix24.</p><ErrorBanner message={error} />{authors.length ? authors.map((author) => <div className="manual-authors__row" key={author.id}><span><strong>{author.full_name}</strong><small>{[author.company, author.department, author.position].filter(Boolean).join(', ') || 'Дополнительных данных нет'}</small></span><Button variant="ghost" type="button" onClick={() => edit(author)}>Редактировать</Button></div>) : <p className="hint">Подтверждённых авторов пока нет.</p>}</section>
}
