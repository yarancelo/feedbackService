// Public page: submit anonymous feedback.
import { useState } from 'react'
import { Link } from 'react-router-dom'
import { createFeedback } from '../api/feedback.js'
import Button from '../components/Button.jsx'
import ErrorBanner from '../components/ErrorBanner.jsx'
import Field from '../components/Field.jsx'
import { logger } from '../lib/logger.js'

export default function FeedbackForm() {
  const [topic, setTopic] = useState('')
  const [body, setBody] = useState('')
  const [status, setStatus] = useState('idle') // idle | sending | done
  const [error, setError] = useState('')

  const canSend = topic.trim() !== '' && body.trim() !== '' && status !== 'sending'

  async function submit(e) {
    e.preventDefault()
    if (!canSend) return
    setStatus('sending')
    setError('')
    logger.info('Submitting anonymous feedback')
    try {
      await createFeedback(topic.trim(), body.trim())
      setStatus('done')
    } catch (err) {
      logger.error('Feedback submission failed', err.message)
      setError(err.message)
      setStatus('idle')
    }
  }

  function reset() {
    setTopic('')
    setBody('')
    setError('')
    setStatus('idle')
  }

  return (
    <div className="wrap">
      <div className="compose">
        <div className="compose__head">
          <div className="brand">
            {/* Логотип: положите файл в frontend/public/logo.svg — появится здесь.
                Пока файла нет, слот скрывается через onError. */}
            <img
              src="/logo.svg"
              alt="kravt h&h"
              className="brand__logo"
              onError={(e) => {
                e.currentTarget.style.display = 'none'
              }}
            />
            <span className="brand__name">kravt h&h</span>
          </div>
          <h1 className="compose__title">Банк идей и предложений</h1>
          <p className="compose__lede">
            Это пространство для вашей обратной связи. Здесь вы можете написать свои
            идеи, рассказать о том, что какой-то рабочий процесс работает неправильно и
            предложить его улучшить, поделиться радостью от работы в компании или тем,
            на что стоит обратить внимание.
          </p>
        </div>

        <div className="card">
          {status === 'done' ? (
            <div className="sent">
              <div className="sent__mark" aria-hidden="true">
                <svg viewBox="0 0 24 24"><path d="M5 13l4 4L19 7" /></svg>
              </div>
              <h2 className="sent__title">Отзыв отправлен</h2>
              <p className="sent__text">
                Он лёг в общий ящик без каких-либо данных о вас. Спасибо, что нашли
                время написать.
              </p>
              <Button variant="ghost" onClick={reset}>Написать ещё</Button>
            </div>
          ) : (
            <form onSubmit={submit} className="fade-in" noValidate>
              <ErrorBanner message={error} />
              <Field id="topic" label="Тема" value={topic} onChange={setTopic}
                     maxLength={500} placeholder="Коротко о сути" />
              <Field id="body" label="Текст отзыва" value={body} onChange={setBody}
                     textarea placeholder="Опишите подробнее — что происходит и что можно улучшить" />
              <div className="row-between">
                <span className="hint">Тема и текст обязательны</span>
                <Button variant="primary" type="submit" disabled={!canSend}>
                  {status === 'sending' ? 'Отправляем…' : 'Отправить анонимно'}
                </Button>
              </div>
            </form>
          )}
        </div>

        <p className="footlink"><Link to="/admin">Вход для администратора</Link></p>
      </div>
    </div>
  )
}
