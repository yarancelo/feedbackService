import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { BrowserRouter } from 'react-router-dom'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import Wall from '../../src/pages/Wall.jsx'
import * as ideasApi from '../../src/api/ideas.js'

const idea = { id: '1', topic: 'Кофе', body: 'Поставить кофемашину', category: 'Сервис', author_name: 'Иван', author_department: 'Ресепшен', likes: 2, dislikes: 0, viewer_reaction: 0, status: 'new' }

describe('Wall', () => {
  beforeEach(() => vi.spyOn(ideasApi, 'listWall').mockResolvedValue({ items: [idea], total_pages: 1 }))
  it('renders submitted ideas and their author', async () => {
    render(<BrowserRouter><Wall /></BrowserRouter>)
    expect(await screen.findByText('Кофе')).toBeInTheDocument()
    expect(screen.getByText('Иван · Ресепшен')).toBeInTheDocument()
    expect(screen.getByText('На рассмотрении')).toBeInTheDocument()
  })
  it('sends a browser reaction', async () => {
    const user = userEvent.setup()
    vi.spyOn(ideasApi, 'reactToIdea').mockResolvedValue({ ...idea, likes: 3, viewer_reaction: 1 })
    render(<BrowserRouter><Wall /></BrowserRouter>)
    await user.click(await screen.findByRole('button', { name: /👍 2/ }))
    expect(ideasApi.reactToIdea).toHaveBeenCalledWith('1', 1)
  })
})
