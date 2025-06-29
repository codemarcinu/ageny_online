import { render, screen } from '@testing-library/react'
import ProductsSection from './ProductsSection'
import { ApiProvider } from '../../contexts/ApiContext'
import { GamificationProvider } from '../../contexts/GamificationContext'

describe('ProductsSection', () => {
  it('renders without crashing', () => {
    render(
      <ApiProvider>
        <GamificationProvider>
          <ProductsSection />
        </GamificationProvider>
      </ApiProvider>
    )
    expect(screen.getByText(/produkty/i)).toBeInTheDocument()
  })
}) 