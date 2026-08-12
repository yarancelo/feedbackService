// Admin login form.
import { useState } from 'react'
import { Link } from 'react-router-dom'
import Button from '../../components/Button.jsx'
import ErrorBanner from '../../components/ErrorBanner.jsx'
import Field from '../../components/Field.jsx'
import { logger } from '../../lib/logger.js'

export default function LoginForm({ onLogin }) {
  const [login, setLogin] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  async function submit(e) {
    e.preventDefault()
    setBusy(true)
    setError('')
    try {
      await onLogin(login, password)
    } catch (err) {
      logger.warn('Login rejected', err.status)
      setError(err.status === 401 ? 'Неверный логин или пароль' : err.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="wrap">
      <div className="login">
        <Link className="form-close" to="/" aria-label="Закрыть">×</Link>
        <div className="card" style={{ marginTop: 10 }}>
          <h1 className="login__title">Вход для администратора</h1>
          <p className="login__lede">Модерация идей и работа с обратной связью.</p>
          <form onSubmit={submit} noValidate>
            <ErrorBanner message={error} />
            <Field id="login" label="Логин" value={login} onChange={setLogin}
                   autoComplete="username" />
            <Field id="password" label="Пароль" type="password" value={password}
                   onChange={setPassword} autoComplete="current-password" />
            <div className="row-between">
              <Link to="/" className="hint">← Вернуться к обратной связи</Link>
              <Button variant="primary" type="submit" disabled={busy || !login || !password}>
                {busy ? 'Входим…' : 'Войти'}
              </Button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}
