import { useEffect, useState } from 'react'
import { searchEmployees } from '../api/employees.js'

export default function AuthorPicker({ value, manualValue, onChange, onManualChange, disabled }) {
  const [query, setQuery] = useState(manualValue || ''); const [matches, setMatches] = useState([]); const [open, setOpen] = useState(false); const [loading, setLoading] = useState(false)
  useEffect(() => { const text = (manualValue || query).trim(); if (text.length < 3) { setMatches([]); return }; const timer = setTimeout(async () => { setLoading(true); try { setMatches(await searchEmployees(text)) } catch { setMatches([]) } finally { setLoading(false) } }, 250); return () => clearTimeout(timer) }, [manualValue, query])
  if (disabled) return null
  return <div className="field author-picker"><label className="label" htmlFor="author">Автор</label><input id="author" className="input" value={manualValue || query} placeholder="Начните вводить ФИО" autoComplete="off" onFocus={() => setOpen(true)} onChange={(e) => { setQuery(e.target.value); onChange(null); onManualChange(e.target.value); setOpen(true) }} />{open && (manualValue || query).trim().length >= 3 && <div className="picker" role="listbox">{loading ? <p className="picker__empty">Ищем...</p> : matches.length ? matches.map((employee) => <button key={employee.bitrix_id} type="button" role="option" onMouseDown={(e) => e.preventDefault()} onClick={() => { onChange(employee.bitrix_id); onManualChange(''); setQuery(employee.full_name); setOpen(false) }}><strong>{employee.full_name}</strong></button>) : <p className="picker__empty">Сотрудник не найден. Можно оставить введенное ФИО.</p>}</div>}<p className="hint">Введите минимум 3 символа для поиска или укажите ФИО вручную.</p></div>
}
