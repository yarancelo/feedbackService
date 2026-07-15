import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import ErrorBanner from '../../src/components/ErrorBanner.jsx'

describe('ErrorBanner', () => {
  it('renders nothing without a message', () => {
    const { container } = render(<ErrorBanner message="" />)
    expect(container).toBeEmptyDOMElement()
  })

  it('renders the message', () => {
    render(<ErrorBanner message="Ошибка" />)
    expect(screen.getByRole('alert')).toHaveTextContent('Ошибка')
  })
})
