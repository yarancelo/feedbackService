import { useEffect, useMemo, useState } from 'react'
import { listEmployees } from '../api/employees.js'

export default function AuthorPicker({ value, onChange, disabled }) {
  const [employees, setEmployees] = useState([])
  const [query, setQuery] = useState('')
  const [open, setOpen] = useState(false)
  const selected = employees.find((item) => item.bitrix_id === value)
  const usingStub = employees.some((item) => item.bitrix_id.startsWith('stub-'))
  const matches = useMemo(() => employees.filter((item) => item.full_name.toLowerCase().includes(query.toLowerCase())).slice(0, 8), [employees, query])

  useEffect(() => {
    listEmployees().then(setEmployees).catch(() => setEmployees([]))
  }, [])

  if (disabled) return null

  return (
    <div className="field author-picker">
      <label className="label" htmlFor="author">Автор</label>
      <input
        id="author"
        className="input"
        value={selected?.full_name ?? query}
        placeholder="Начните вводить ФИО"
        autoComplete="off"
        onFocus={() => setOpen(true)}
        onChange={(event) => { setQuery(event.target.value); onChange(null); setOpen(true) }}
      />
      {usingStub && <p className="form-note">Справочник Bitrix пока не подключён: показаны тестовые сотрудники. Добавьте BITRIX_WEBHOOK_URL на сервере, чтобы выбрать реального автора.</p>}
      {open && !selected && query && (
        <div className="picker" role="listbox">
          {matches.length ? matches.map((employee) => (
            <button key={employee.bitrix_id} type="button" role="option" onMouseDown={(event) => event.preventDefault()} onClick={() => { onChange(employee.bitrix_id); setQuery(''); setOpen(false) }}>
              <strong>{employee.full_name}</strong>
              <small>{[employee.company, employee.department].filter(Boolean).join(', ') || employee.position}</small>
            </button>
          )) : <p className="picker__empty">Сотрудник не найден</p>}
        </div>
      )}
      {selected && <p className="hint">{[selected.company, selected.department].filter(Boolean).join(', ')}</p>}
    </div>
  )
}
