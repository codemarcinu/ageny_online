import { createContext, useContext, useState, useEffect, ReactNode } from 'react'

interface HealthStatus {
  status: 'healthy' | 'unhealthy' | 'loading'
  app?: {
    name: string
    version: string
    environment: string
  }
  agent?: {
    status: string
    provider: string
  }
  providers?: Record<string, any>
  error?: string
}

interface HealthContextType {
  healthStatus: HealthStatus
  refreshHealth: () => Promise<void>
  isLoading: boolean
}

const HealthContext = createContext<HealthContextType | undefined>(undefined)

export function HealthProvider({ children }: { children: ReactNode }) {
  const [healthStatus, setHealthStatus] = useState<HealthStatus>({ status: 'loading' })
  const [isLoading, setIsLoading] = useState(false)

  const checkHealth = async () => {
    try {
      setIsLoading(true)
      const response = await fetch('/health')
      const data = await response.json()
      
      setHealthStatus({
        status: data.status,
        app: data.app,
        agent: data.agent,
        providers: data.providers,
      })
    } catch (error: any) {
      setHealthStatus({
        status: 'unhealthy',
        error: error.message || 'Failed to check health status',
      })
    } finally {
      setIsLoading(false)
    }
  }

  const refreshHealth = async () => {
    await checkHealth()
  }

  useEffect(() => {
    checkHealth()
    
    // Check health every 30 seconds
    const interval = setInterval(checkHealth, 30000)
    return () => clearInterval(interval)
  }, [])

  return (
    <HealthContext.Provider value={{ healthStatus, refreshHealth, isLoading }}>
      {children}
    </HealthContext.Provider>
  )
}

export function useHealth() {
  const context = useContext(HealthContext)
  if (context === undefined) {
    throw new Error('useHealth must be used within a HealthProvider')
  }
  return context
} 