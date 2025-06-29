import { render, screen } from '@testing-library/react'
import AchievementsPanel from './AchievementsPanel'
import { GamificationProvider } from '../../contexts/GamificationContext'

describe('AchievementsPanel', () => {
  it('renders without crashing', () => {
    render(
      <GamificationProvider>
        <AchievementsPanel />
      </GamificationProvider>
    )
    expect(screen.getByText(/osiągnięcia/i)).toBeInTheDocument()
  })

  it('displays achievements list', () => {
    render(
      <GamificationProvider>
        <AchievementsPanel />
      </GamificationProvider>
    )
    expect(screen.getByText(/pierwszy krok/i)).toBeInTheDocument()
  })
}) 