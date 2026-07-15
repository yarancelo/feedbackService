// Authentication state: token presence + login/logout actions.
import { useCallback, useState } from 'react'
import { login as loginRequest } from '../api/auth.js'
import { logger } from '../lib/logger.js'
import { clearToken, getToken, setToken } from '../lib/token.js'

export function useAuth() {
  const [authed, setAuthed] = useState(Boolean(getToken()))

  const login = useCallback(async (loginValue, password) => {
    logger.info('Attempting admin login', loginValue)
    const { access_token: token } = await loginRequest(loginValue, password)
    setToken(token)
    setAuthed(true)
    logger.info('Admin login succeeded')
  }, [])

  const logout = useCallback(() => {
    logger.info('Admin logout')
    clearToken()
    setAuthed(false)
  }, [])

  return { authed, login, logout }
}
