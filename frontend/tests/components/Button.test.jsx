import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import Button from '../../src/components/Button.jsx'

describe('Button', () => {
  it('applies the variant class', () => {
    render(<Button variant="danger">X</Button>)
    expect(screen.getByRole('button')).toHaveClass('btn--danger')
  })

  it('fires onClick', async () => {
    const onClick = vi.fn()
    render(<Button onClick={onClick}>Go</Button>)
    await userEvent.click(screen.getByRole('button'))
    expect(onClick).toHaveBeenCalled()
  })
})
