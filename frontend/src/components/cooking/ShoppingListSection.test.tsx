import { render, screen } from '@testing-library/react'
import ShoppingListSection from './ShoppingListSection'
import { ApiProvider } from '../../contexts/ApiContext'
import { GamificationProvider } from '../../contexts/GamificationContext'

describe('ShoppingListSection', () => {
  it('renders without crashing', () => {
    render(
      <ApiProvider>
        <GamificationProvider>
          <ShoppingListSection />
        </GamificationProvider>
      </ApiProvider>
    )
    expect(screen.getByText(/listy zakupów/i)).toBeInTheDocument()
  })

  it('displays loading state', () => {
    render(
      <ApiProvider>
        <GamificationProvider>
          <ShoppingListSection />
        </GamificationProvider>
      </ApiProvider>
    )
    expect(screen.getByText(/ładowanie list zakupów/i)).toBeInTheDocument()
  })
}) 