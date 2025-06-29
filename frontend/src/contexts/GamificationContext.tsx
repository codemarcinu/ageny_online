import React, { createContext, useContext, useState, useEffect } from 'react'

interface Achievement {
  id: string
  name: string
  description: string
  icon: string
  points: number
  unlocked: boolean
  unlockedAt?: Date
}

interface Challenge {
  id: string
  name: string
  description: string
  type: 'daily' | 'weekly' | 'monthly'
  progress: number
  target: number
  completed: boolean
  points: number
  expiresAt: Date
}

interface GamificationState {
  points: number
  level: number
  experience: number
  achievements: Achievement[]
  challenges: Challenge[]
  streak: number
  lastActivity: Date
}

interface GamificationContextType {
  state: GamificationState
  addPoints: (amount: number) => void
  unlockAchievement: (achievementId: string) => void
  updateChallengeProgress: (challengeId: string, progress: number) => void
  getLevelProgress: () => { current: number; next: number; percentage: number }
  resetDailyChallenges: () => void
  showConfetti: boolean
  triggerConfetti: () => void
}

const GamificationContext = createContext<GamificationContextType | undefined>(undefined)

const INITIAL_ACHIEVEMENTS: Achievement[] = [
  {
    id: 'first-chat',
    name: 'Pierwszy krok! 🎉',
    description: 'Rozpocznij pierwszą rozmowę z AI',
    icon: '💬',
    points: 50,
    unlocked: false
  },
  {
    id: 'chat-master',
    name: 'Mistrz rozmów! 🗣️',
    description: 'Przeprowadź 10 rozmów z AI',
    icon: '👑',
    points: 200,
    unlocked: false
  },
  {
    id: 'ocr-explorer',
    name: 'Eksplorator dokumentów! 📄',
    description: 'Przeskanuj swój pierwszy dokument',
    icon: '📷',
    points: 100,
    unlocked: false
  },
  {
    id: 'streak-3',
    name: 'Konsekwentna! 🔥',
    description: 'Używaj aplikacji przez 3 dni z rzędu',
    icon: '🔥',
    points: 150,
    unlocked: false
  },
  {
    id: 'streak-7',
    name: 'Nieustraszona! ⚡',
    description: 'Używaj aplikacji przez 7 dni z rzędu',
    icon: '⚡',
    points: 500,
    unlocked: false
  },
  {
    id: 'points-1000',
    name: 'Punktowa gwiazda! ⭐',
    description: 'Zdobądź 1000 punktów',
    icon: '⭐',
    points: 300,
    unlocked: false
  }
]

const DAILY_CHALLENGES: Omit<Challenge, 'progress' | 'completed' | 'expiresAt'>[] = [
  {
    id: 'daily-chat-3',
    name: 'Rozmowa z AI',
    description: 'Przeprowadź 3 rozmowy z AI',
    type: 'daily',
    target: 3,
    points: 100
  },
  {
    id: 'daily-ocr-1',
    name: 'Skanowanie dokumentów',
    description: 'Przeskanuj 1 dokument',
    type: 'daily',
    target: 1,
    points: 75
  },
  {
    id: 'daily-streak',
    name: 'Codzienna aktywność',
    description: 'Używaj aplikacji dzisiaj',
    type: 'daily',
    target: 1,
    points: 50
  }
]

export function GamificationProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<GamificationState>(() => {
    const saved = localStorage.getItem('ageny-teen-gamification')
    if (saved) {
      return JSON.parse(saved)
    }
    
    return {
      points: 0,
      level: 1,
      experience: 0,
      achievements: INITIAL_ACHIEVEMENTS,
      challenges: [],
      streak: 0,
      lastActivity: new Date()
    }
  })

  const [showConfetti, setShowConfetti] = useState(false)

  useEffect(() => {
    localStorage.setItem('ageny-teen-gamification', JSON.stringify(state))
  }, [state])

  useEffect(() => {
    // Sprawdź czy minął dzień i zresetuj daily challenges
    const now = new Date()
    const lastActivity = new Date(state.lastActivity)
    const daysDiff = Math.floor((now.getTime() - lastActivity.getTime()) / (1000 * 60 * 60 * 24))
    
    if (daysDiff >= 1) {
      resetDailyChallenges()
    }
  }, [state.lastActivity])

  const addPoints = (amount: number) => {
    setState(prev => {
      const newPoints = prev.points + amount
      let newExperience = prev.experience + amount
      const experienceForNextLevel = prev.level * 100
      
      let newLevel = prev.level
      
      if (newExperience >= experienceForNextLevel) {
        newLevel = prev.level + 1
        newExperience = newExperience - experienceForNextLevel
        // Trigger confetti for level up
        triggerConfetti()
      }
      
      return {
        ...prev,
        points: newPoints,
        level: newLevel,
        experience: newExperience,
        lastActivity: new Date()
      }
    })
  }

  const unlockAchievement = (achievementId: string) => {
    setState(prev => {
      const achievement = prev.achievements.find(a => a.id === achievementId)
      if (!achievement || achievement.unlocked) return prev
      
      const updatedAchievements = prev.achievements.map(a =>
        a.id === achievementId
          ? { ...a, unlocked: true, unlockedAt: new Date() }
          : a
      )
      
      // Trigger confetti for achievement unlock
      triggerConfetti()
      
      return {
        ...prev,
        achievements: updatedAchievements,
        points: prev.points + achievement.points,
        experience: prev.experience + achievement.points
      }
    })
  }

  const updateChallengeProgress = (challengeId: string, progress: number) => {
    setState(prev => {
      const updatedChallenges = prev.challenges.map(c =>
        c.id === challengeId
          ? { ...c, progress: Math.min(progress, c.target), completed: progress >= c.target }
          : c
      )
      
      // Sprawdź czy challenge został ukończony
      const challenge = updatedChallenges.find(c => c.id === challengeId)
      if (challenge && challenge.completed && !challenge.completed) {
        addPoints(challenge.points)
        triggerConfetti()
      }
      
      return {
        ...prev,
        challenges: updatedChallenges
      }
    })
  }

  const getLevelProgress = () => {
    const experienceForNextLevel = state.level * 100
    const percentage = (state.experience / experienceForNextLevel) * 100
    
    return {
      current: state.experience,
      next: experienceForNextLevel,
      percentage: Math.min(percentage, 100)
    }
  }

  const resetDailyChallenges = () => {
    const tomorrow = new Date()
    tomorrow.setDate(tomorrow.getDate() + 1)
    tomorrow.setHours(0, 0, 0, 0)
    
    const newChallenges: Challenge[] = DAILY_CHALLENGES.map(challenge => ({
      ...challenge,
      progress: 0,
      completed: false,
      expiresAt: tomorrow
    }))
    
    setState(prev => ({
      ...prev,
      challenges: newChallenges,
      lastActivity: new Date()
    }))
  }

  const triggerConfetti = () => {
    setShowConfetti(true)
    setTimeout(() => setShowConfetti(false), 100)
  }

  return (
    <GamificationContext.Provider
      value={{
        state,
        addPoints,
        unlockAchievement,
        updateChallengeProgress,
        getLevelProgress,
        resetDailyChallenges,
        showConfetti,
        triggerConfetti
      }}
    >
      {children}
    </GamificationContext.Provider>
  )
}

export function useGamification() {
  const context = useContext(GamificationContext)
  if (context === undefined) {
    throw new Error('useGamification must be used within a GamificationProvider')
  }
  return context
} 