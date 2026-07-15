import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'
import FeedbackForm from '../../src/pages/FeedbackForm.jsx'
import * as feedbackApi from '../../src/api/feedback.js'

function renderForm() {
  return render(
    <MemoryRouter>
      <FeedbackForm />
    </MemoryRouter>,
  )
}

afterEach(() => vi.restoreAllMocks())

describe('FeedbackForm', () => {
  it('disables submit until topic and body are filled', async () => {
    renderForm()
    const submit = screen.getByRole('button', { name: /Отправить/ })
    expect(submit).toBeDisabled()

    await userEvent.type(screen.getByLabelText('Тема'), 'Кофе')
    expect(submit).toBeDisabled()
    await userEvent.type(screen.getByLabelText('Текст отзыва'), 'Нужна машина')
    expect(submit).toBeEnabled()
  })

  it('shows the confirmation after a successful submit', async () => {
    vi.spyOn(feedbackApi, 'createFeedback').mockResolvedValue({ id: '1' })
    renderForm()
    await userEvent.type(screen.getByLabelText('Тема'), 'Кофе')
    await userEvent.type(screen.getByLabelText('Текст отзыва'), 'Нужна машина')
    await userEvent.click(screen.getByRole('button', { name: /Отправить/ }))

    await waitFor(() => expect(screen.getByText('Отзыв отправлен')).toBeInTheDocument())
    expect(feedbackApi.createFeedback).toHaveBeenCalledWith('Кофе', 'Нужна машина')
  })
})
