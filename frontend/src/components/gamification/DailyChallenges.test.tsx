import { render, screen } from '@testing-library/react'
import DailyChallenges from './DailyChallenges'
import { GamificationProvider } from '../../contexts/GamificationContext'

describe('DailyChallenges', () => {
  it('renders default empty state', () => {
    render(
      <GamificationProvider>
        <DailyChallenges />
      </GamificationProvider>
    )
    expect(screen.getByText(/dzisiejsze wyzwania/i)).toBeInTheDocument()
    expect(screen.getByText(/brak aktywnych wyzwań/i)).toBeInTheDocument()
  })
}) 