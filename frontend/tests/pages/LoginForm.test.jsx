import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it, vi } from 'vitest'
import LoginForm from '../../src/pages/Admin/LoginForm.jsx'

function renderLogin(onLogin) {
  return render(<MemoryRouter><LoginForm onLogin={onLogin} /></MemoryRouter>)
}

describe('LoginForm', () => {
  it('calls onLogin with the entered credentials', async () => {
    const onLogin = vi.fn().mockResolvedValue()
    renderLogin(onLogin)
    await userEvent.type(screen.getByLabelText('Логин'), 'admin')
    await userEvent.type(screen.getByLabelText('Пароль'), 'password')
    await userEvent.click(screen.getByRole('button', { name: 'Войти' }))
    expect(onLogin).toHaveBeenCalledWith('admin', 'password')
  })

  it('shows an error message on 401', async () => {
    const onLogin = vi.fn().mockRejectedValue({ status: 401 })
    renderLogin(onLogin)
    await userEvent.type(screen.getByLabelText('Логин'), 'admin')
    await userEvent.type(screen.getByLabelText('Пароль'), 'wrong')
    await userEvent.click(screen.getByRole('button', { name: 'Войти' }))
    await waitFor(() => expect(screen.getByText('Неверный логин или пароль')).toBeInTheDocument())
  })
})
