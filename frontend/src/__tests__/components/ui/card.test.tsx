import { render, screen } from '@testing-library/react'
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
} from '@/components/ui/card'

describe('Card Components', () => {
  describe('Card', () => {
    it('renders correctly', () => {
      render(<Card data-testid="card">Card Content</Card>)
      expect(screen.getByTestId('card')).toBeInTheDocument()
    })

    it('applies correct classes', () => {
      render(<Card data-testid="card">Card Content</Card>)
      const card = screen.getByTestId('card')
      expect(card).toHaveClass('border', 'bg-card')
    })
  })

  describe('CardHeader', () => {
    it('renders correctly', () => {
      render(
        <Card>
          <CardHeader data-testid="card-header">Header Content</CardHeader>
        </Card>
      )
      expect(screen.getByTestId('card-header')).toBeInTheDocument()
    })
  })

  describe('CardTitle', () => {
    it('renders with correct heading level', () => {
      render(
        <Card>
          <CardHeader>
            <CardTitle>Test Title</CardTitle>
          </CardHeader>
        </Card>
      )
      expect(screen.getByText('Test Title')).toBeInTheDocument()
    })
  })

  describe('CardDescription', () => {
    it('renders correctly', () => {
      render(
        <Card>
          <CardHeader>
            <CardDescription>Test Description</CardDescription>
          </CardHeader>
        </Card>
      )
      expect(screen.getByText('Test Description')).toBeInTheDocument()
    })
  })

  describe('Full Card Example', () => {
    it('renders complete card structure', () => {
      render(
        <Card>
          <CardHeader>
            <CardTitle>Test Title</CardTitle>
            <CardDescription>Test Description</CardDescription>
          </CardHeader>
          <CardContent>
            <p>Test Content</p>
          </CardContent>
          <CardFooter>
            <button>Test Button</button>
          </CardFooter>
        </Card>
      )

      expect(screen.getByText('Test Title')).toBeInTheDocument()
      expect(screen.getByText('Test Description')).toBeInTheDocument()
      expect(screen.getByText('Test Content')).toBeInTheDocument()
      expect(screen.getByRole('button', { name: 'Test Button' })).toBeInTheDocument()
    })
  })
})
