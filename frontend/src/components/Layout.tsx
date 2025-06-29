import { ReactNode } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { MessageSquare, FileText, Server, Activity, Home, Search, Sparkles } from 'lucide-react'
import { useHealth } from '../contexts/HealthContext'
import { useGamification } from '../contexts/GamificationContext'

interface LayoutProps {
  children: ReactNode
}

export default function Layout({ children }: LayoutProps) {
  const location = useLocation()
  const { healthStatus } = useHealth()
  const { state } = useGamification()

  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: Home },
    { name: 'Chat', href: '/chat', icon: MessageSquare },
    { name: 'OCR', href: '/ocr', icon: FileText },
    { name: 'Web Search', href: '/web-search', icon: Search },
    { name: 'Providers', href: '/providers', icon: Server },
  ]

  const isActive = (path: string) => location.pathname === path

  return (
    <div className="min-h-screen bg-gradient-to-br from-teen-pink-50 to-teen-purple-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-teen-purple-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <div className="flex items-center space-x-2">
                <Sparkles className="w-6 h-6 text-teen-purple-500" />
                <h1 className="text-xl font-bold bg-gradient-to-r from-teen-pink-600 to-teen-purple-600 bg-clip-text text-transparent">
                  Ageny Teen
                </h1>
              </div>
              <div className="ml-4 flex items-center">
                <Activity 
                  className={`w-4 h-4 mr-2 ${
                    healthStatus.status === 'healthy' 
                      ? 'text-teen-mint-500' 
                      : healthStatus.status === 'unhealthy' 
                      ? 'text-red-500' 
                      : 'text-teen-yellow-500'
                  }`} 
                />
                <span className={`text-sm font-medium ${
                  healthStatus.status === 'healthy' 
                    ? 'text-teen-mint-700' 
                    : healthStatus.status === 'unhealthy' 
                    ? 'text-red-700' 
                    : 'text-teen-yellow-700'
                }`}>
                  {healthStatus.status === 'healthy' ? 'Online' : 
                   healthStatus.status === 'unhealthy' ? 'Offline' : 'Checking...'}
                </span>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              {/* Points Display */}
              <div className="flex items-center space-x-2 bg-gradient-to-r from-teen-pink-100 to-teen-purple-100 px-3 py-1 rounded-full">
                <span className="text-teen-purple-700 font-medium">⭐ {state.points}</span>
                <span className="text-teen-purple-600 text-sm">pkt</span>
              </div>
              
              {healthStatus.app && (
                <div className="text-sm text-teen-purple-500">
                  v{healthStatus.app.version} • {healthStatus.app.environment}
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-white border-b border-teen-purple-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            {navigation.map((item) => {
              const Icon = item.icon
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`flex items-center px-3 py-4 text-sm font-medium border-b-2 transition-all duration-200 ${
                    isActive(item.href)
                      ? 'border-teen-purple-500 text-teen-purple-600 bg-teen-purple-50'
                      : 'border-transparent text-teen-purple-500 hover:text-teen-purple-700 hover:border-teen-purple-300 hover:bg-teen-purple-25'
                  }`}
                >
                  <Icon className="w-4 h-4 mr-2" />
                  {item.name}
                </Link>
              )
            })}
          </div>
        </div>
      </nav>

      {/* Main content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>
    </div>
  )
} 