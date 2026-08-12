import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { BrowserRouter } from 'react-router-dom'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import FeedbackForm from '../../src/pages/FeedbackForm.jsx'
import * as ideasApi from '../../src/api/ideas.js'
import * as employeesApi from '../../src/api/employees.js'

function renderPage() { return render(<BrowserRouter><FeedbackForm /></BrowserRouter>) }

describe('FeedbackForm', () => {
  beforeEach(() => vi.spyOn(employeesApi, 'listEmployees').mockResolvedValue([]))

  it('requires text before submitting', () => {
    renderPage()
    expect(screen.getByRole('button', { name: 'Опубликовать идею' })).toBeDisabled()
  })

  it('submits an anonymous idea', async () => {
    const user = userEvent.setup()
    vi.spyOn(ideasApi, 'createIdea').mockResolvedValue({ id: '1' })
    renderPage()
    await user.type(screen.getByLabelText('Расскажите подробнее'), 'Нужна кофемашина')
    await user.click(screen.getByRole('button', { name: 'Опубликовать идею' }))
    expect(ideasApi.createIdea).toHaveBeenCalledWith(expect.objectContaining({ body: 'Нужна кофемашина', visibility: 'anonymous', author_bitrix_id: null }))
    expect(await screen.findByText('Идея опубликована')).toBeInTheDocument()
  })
})
