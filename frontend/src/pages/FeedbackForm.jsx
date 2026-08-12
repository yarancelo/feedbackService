import { useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { createIdea } from '../api/ideas.js'
import AuthorPicker from '../components/AuthorPicker.jsx'
import Button from '../components/Button.jsx'
import ErrorBanner from '../components/ErrorBanner.jsx'
import Field from '../components/Field.jsx'

const VISIBILITIES = [
  ['anonymous', 'Анонимно', 'Без имени. Идея не участвует в выборе идеи недели.'],
  ['private', 'Скрыть имя', 'Имя увидит только администратор. Идея сможет участвовать в выборе идеи недели.'],
  ['public', 'Показать имя', 'Имя и отдел будут видны на стене.'],
]

export default function FeedbackForm() {
  const [searchParams] = useSearchParams()
  const isFeedback = searchParams.get('type') === 'feedback'
  const defaultCategory = isFeedback ? 'Обратная связь' : 'Идея'
  const [form, setForm] = useState({ topic: '', body: '', category: defaultCategory, visibility: 'anonymous', authorId: null, authorName: '' })
  const [state, setState] = useState('editing')
  const [error, setError] = useState('')
  const named = form.visibility !== 'anonymous'
  const set = (name) => (value) => setForm((current) => ({ ...current, [name]: value }))
  const canSubmit = form.body.trim() && (!named || form.authorId || form.authorName.trim()) && state !== 'sending'

  async function submit(event) {
    event.preventDefault()
    if (!canSubmit) return
    setState('sending')
    setError('')
    try {
      await createIdea({
        topic: form.topic.trim() || null,
        body: form.body.trim(),
        category: form.category.trim() || null,
        visibility: form.visibility,
        author_bitrix_id: form.authorId,
        author_name: form.authorId ? null : form.authorName.trim() || null,
      })
      setState('sent')
    } catch (requestError) {
      setError(requestError.message)
      setState('editing')
    }
  }

  function reset() {
    setForm({ topic: '', body: '', category: defaultCategory, visibility: 'anonymous', authorId: null, authorName: '' })
    setError('')
    setState('editing')
  }

  return (
    <div className="wrap">
      <main className="compose">
        <header className="compose__head">
          <Link className="form-close" to="/" aria-label="Закрыть">×</Link>
          <p className="eyebrow">Стена идей</p>
          <h1 className="compose__title">{isFeedback ? 'Оставить отзыв' : 'Предложить идею'}</h1>
          <p className="compose__lede">Одна идея - один стикер. Не обязательно предлагать что-то большое: небольшие улучшения тоже важны.</p>
        </header>
        <section className="card">
          {state === 'sent' ? (
            <div className="sent">
              <div className="sent__mark" aria-hidden="true">✓</div>
              <h2 className="sent__title">Идея опубликована</h2>
              <p className="sent__text">Идея уже на стене со статусом «На рассмотрении». После модерации принятые идеи с указанным автором смогут участвовать в выборе идеи недели.</p>
              <Button type="button" onClick={reset}>Предложить ещё идею</Button>
            </div>
          ) : (
            <form onSubmit={submit} noValidate>
              <ErrorBanner message={error} />
              <Field id="topic" label="Название идеи" value={form.topic} onChange={set('topic')} maxLength={500} placeholder="Сформулируйте идею в нескольких словах" />
              <Field id="body" label="Расскажите подробнее" value={form.body} onChange={set('body')} textarea placeholder="Что предлагаете изменить и почему это будет полезно?" />
              {!isFeedback && <Field id="category" label="Категория" value={form.category} onChange={set('category')} maxLength={100} placeholder="Например: сервис, процессы или команда" />}
              <fieldset className="visibility">
                <legend className="label">Как указать автора?</legend>
                {VISIBILITIES.map(([value, title, hint]) => (
                  <label className="visibility__option" key={value}>
                    <input type="radio" name="visibility" value={value} checked={form.visibility === value} onChange={() => setForm((current) => ({ ...current, visibility: value, authorId: value === 'anonymous' ? null : current.authorId, authorName: value === 'anonymous' ? '' : current.authorName }))} />
                    <span><strong>{title}</strong><small>{hint}</small></span>
                  </label>
                ))}
              </fieldset>
              <AuthorPicker value={form.authorId} manualValue={form.authorName} onChange={set('authorId')} onManualChange={set('authorName')} disabled={!named} />
              {named && !form.authorId && !form.authorName.trim() && <p className="form-note">Выберите сотрудника или укажите ФИО.</p>}
              <div className="row-between">
                <span className="hint">Полезные и оригинальные идеи могут стать идеей недели.</span>
                <Button type="submit" disabled={!canSubmit}>{state === 'sending' ? 'Отправляем…' : 'Опубликовать идею'}</Button>
              </div>
            </form>
          )}
        </section>
        <p className="footlink"><Link to="/">Вернуться к стене идей</Link> · <Link to="/admin">Вход для администратора</Link></p>
      </main>
    </div>
  )
}
