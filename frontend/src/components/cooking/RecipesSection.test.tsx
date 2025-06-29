import { render, screen } from '@testing-library/react'
import RecipesSection from './RecipesSection'
import { ApiProvider } from '../../contexts/ApiContext'
import { GamificationProvider } from '../../contexts/GamificationContext'

describe('RecipesSection', () => {
  it('renders without crashing', () => {
    render(
      <ApiProvider>
        <GamificationProvider>
          <RecipesSection />
        </GamificationProvider>
      </ApiProvider>
    )
    expect(screen.getByText(/przepisy kulinarne/i)).toBeInTheDocument()
  })

  it('displays loading state', () => {
    render(
      <ApiProvider>
        <GamificationProvider>
          <RecipesSection />
        </GamificationProvider>
      </ApiProvider>
    )
    expect(screen.getByText(/ładowanie przepisów/i)).toBeInTheDocument()
  })
}) 