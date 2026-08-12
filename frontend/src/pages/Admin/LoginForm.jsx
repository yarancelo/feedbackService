import { useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import Button from '../../components/Button.jsx'
import ErrorBanner from '../../components/ErrorBanner.jsx'
import Field from '../../components/Field.jsx'
import Logo from '../../components/Logo.jsx'
import { logger } from '../../lib/logger.js'

export default function LoginForm({ onLogin }) {
  const [login, setLogin] = useState(''); const [password, setPassword] = useState(''); const [error, setError] = useState(''); const [busy, setBusy] = useState(false); const [shown, setShown] = useState(false); const errorRef = useRef(null)
  async function submit(event) { event.preventDefault(); setBusy(true); setError(''); try { await onLogin(login, password) } catch (err) { logger.warn('Login rejected', err.status); setPassword(''); setError('Неверный логин или пароль'); setTimeout(() => errorRef.current?.focus(), 0) } finally { setBusy(false) } }
  return <div className="wrap"><div className="login"><div className="form-topline"><Logo /><Link className="form-close" to="/" aria-label="Закрыть">×</Link></div><div className="card"><h1 className="login__title">Вход для администратора</h1><form onSubmit={submit} noValidate>{error && <div ref={errorRef} tabIndex="-1"><ErrorBanner message={error} /></div>}<Field id="login" label="Логин" value={login} onChange={setLogin} autoComplete="username" /><div className="password-field"><Field id="password" label="Пароль" type={shown ? 'text' : 'password'} value={password} onChange={setPassword} autoComplete="current-password" /><button className="password-toggle" type="button" onClick={() => setShown((value) => !value)} aria-label={shown ? 'Скрыть пароль' : 'Показать пароль'}>{shown ? 'Скрыть' : 'Показать'}</button></div><div className="row-between"><Link to="/" className="hint">Вернуться на главную</Link><Button variant="primary" type="submit" disabled={busy || !login || !password}>{busy ? 'Входим…' : 'Войти'}</Button></div></form></div></div></div>
}
