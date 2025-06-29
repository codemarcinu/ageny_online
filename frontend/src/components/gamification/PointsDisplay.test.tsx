import { render, screen } from '@testing-library/react'
import PointsDisplay from './PointsDisplay'
import { GamificationProvider } from '../../contexts/GamificationContext'

describe('PointsDisplay', () => {
  it('renders without crashing', () => {
    render(
      <GamificationProvider>
        <PointsDisplay points={100} />
      </GamificationProvider>
    )
    expect(screen.getByText(/100/)).toBeInTheDocument()
  })
}) 