import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Input } from '@/components/ui/input'

describe('Input', () => {
  it('renders correctly', () => {
    render(<Input placeholder="Enter text" />)
    expect(screen.getByPlaceholderText('Enter text')).toBeInTheDocument()
  })

  it('accepts user input', async () => {
    const user = userEvent.setup()
    render(<Input placeholder="Enter text" />)

    const input = screen.getByPlaceholderText('Enter text')
    await user.type(input, 'Hello World')

    expect(input).toHaveValue('Hello World')
  })

  it('can be disabled', () => {
    render(<Input disabled placeholder="Disabled input" />)
    expect(screen.getByPlaceholderText('Disabled input')).toBeDisabled()
  })

  it('handles onChange events', async () => {
    const handleChange = jest.fn()
    const user = userEvent.setup()

    render(<Input onChange={handleChange} placeholder="Enter text" />)

    const input = screen.getByPlaceholderText('Enter text')
    await user.type(input, 'a')

    expect(handleChange).toHaveBeenCalled()
  })

  it('applies correct type attribute', () => {
    render(<Input type="email" placeholder="Enter email" />)
    const input = screen.getByPlaceholderText('Enter email')
    expect(input).toHaveAttribute('type', 'email')
  })

  it('supports different input types', () => {
    const { rerender } = render(<Input type="password" data-testid="input" />)
    expect(screen.getByTestId('input')).toHaveAttribute('type', 'password')

    rerender(<Input type="number" data-testid="input" />)
    expect(screen.getByTestId('input')).toHaveAttribute('type', 'number')
  })
})
