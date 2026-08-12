import { useEffect, useMemo, useState } from 'react'
import { listEmployees } from '../api/employees.js'

export default function AuthorPicker({ value, manualValue, onChange, onManualChange, disabled }) {
  const [employees, setEmployees] = useState([])
  const [query, setQuery] = useState(manualValue || '')
  const [open, setOpen] = useState(false)
  const selected = employees.find((item) => item.bitrix_id === value)
  const matches = useMemo(() => employees.filter((item) => item.full_name.toLowerCase().includes(query.toLowerCase())).slice(0, 8), [employees, query])
  useEffect(() => { listEmployees().then(setEmployees).catch(() => setEmployees([])) }, [])
  useEffect(() => { if (manualValue !== query && !selected) setQuery(manualValue || '') }, [manualValue, selected])
  if (disabled) return null
  function type(value) { setQuery(value); onChange(null); onManualChange(value); setOpen(true) }
  function choose(employee) { onChange(employee.bitrix_id); onManualChange(''); setQuery(''); setOpen(false) }
  return <div className="field author-picker"><label className="label" htmlFor="author">Автор</label><input id="author" className="input" value={selected?.full_name ?? query} placeholder="Начните вводить имя или выберите сотрудника" autoComplete="off" onFocus={() => setOpen(true)} onChange={(event) => type(event.target.value)} />{open && !selected && query && <div className="picker" role="listbox">{matches.map((employee) => <button key={employee.bitrix_id} type="button" role="option" onMouseDown={(event) => event.preventDefault()} onClick={() => choose(employee)}><strong>{employee.full_name}</strong><small>{[employee.company, employee.department].filter(Boolean).join(', ') || employee.position}</small></button>)}{!matches.length && <p className="picker__empty">Не нашли сотрудника? Можно оставить введённое ФИО.</p>}</div>}{selected && <p className="hint">{[selected.company, selected.department].filter(Boolean).join(', ')}</p>}<p className="hint">Нет в списке? Оставьте введённое ФИО.</p></div>
}
