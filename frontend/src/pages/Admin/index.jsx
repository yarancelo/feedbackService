// Admin page: shows login or the feedback list depending on auth state.
import { useAuth } from '../../hooks/useAuth.js'
import FeedbackList from './FeedbackList.jsx'
import LoginForm from './LoginForm.jsx'

export default function Admin() {
  const { authed, login, logout } = useAuth()
  return authed ? <FeedbackList onLogout={logout} /> : <LoginForm onLogin={login} />
}
