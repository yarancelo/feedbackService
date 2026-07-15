import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import Field from '../../src/components/Field.jsx'

describe('Field', () => {
  it('renders a labeled input and reports changes', async () => {
    const onChange = vi.fn()
    render(<Field id="topic" label="Тема" value="" onChange={onChange} />)
    expect(screen.getByLabelText('Тема')).toBeInTheDocument()
    await userEvent.type(screen.getByLabelText('Тема'), 'x')
    expect(onChange).toHaveBeenCalledWith('x')
  })

  it('renders a textarea when requested', () => {
    render(<Field id="body" label="Текст" value="hi" onChange={() => {}} textarea />)
    expect(screen.getByLabelText('Текст').tagName).toBe('TEXTAREA')
  })
})
