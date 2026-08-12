import { useEffect, useState } from 'react'
import { deleteManualAuthor, listManualAuthors, updateManualAuthor } from '../../api/manualAuthors.js'
import Button from '../../components/Button.jsx'

export default function ManualAuthorManager() {
  const [authors, setAuthors] = useState([]); const [error, setError] = useState('')
  const load = () => listManualAuthors().then(setAuthors).catch((requestError) => setError(requestError.message))
  useEffect(() => { load() }, [])
  async function edit(item) { const fullName = window.prompt('ФИО', item.full_name); if (fullName === null || !fullName.trim()) return; const department = window.prompt('Отдел', item.department || ''); if (department === null) return; const company = window.prompt('Компания или отель', item.company || ''); if (company === null) return; try { await updateManualAuthor(item.bitrix_id.replace('manual:', ''), { full_name: fullName.trim(), department: department.trim() || null, company: company.trim() || null }); load() } catch (requestError) { setError(requestError.message) } }
  async function remove(item) { if (!window.confirm(`Удалить ${item.full_name} из локального справочника? Уже отправленные идеи не изменятся.`)) return; try { await deleteManualAuthor(item.bitrix_id.replace('manual:', '')); load() } catch (requestError) { setError(requestError.message) } }
  return <section className="leader-table"><h2>Подтверждённые авторы</h2><p className="hint">Сотрудники, добавленные вручную после проверки.</p>{error && <p className="comments__error" role="alert">{error}</p>}{authors.length ? <table><thead><tr><th>ФИО</th><th>Отдел</th><th>Действия</th></tr></thead><tbody>{authors.map((item) => <tr key={item.bitrix_id}><td>{item.full_name}</td><td>{item.department || item.company || 'Не указан'}</td><td><Button variant="ghost" onClick={() => edit(item)}>Редактировать</Button><Button variant="danger" onClick={() => remove(item)}>Удалить</Button></td></tr>)}</tbody></table> : <p>Подтверждённых авторов пока нет.</p>}</section>
}
