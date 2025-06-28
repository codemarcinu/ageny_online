import { ReactNode } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { MessageSquare, FileText, Server, Activity } from 'lucide-react'
import { useHealth } from '../contexts/HealthContext'

interface LayoutProps {
  children: ReactNode
}

export default function Layout({ children }: LayoutProps) {
  const location = useLocation()
  const { healthStatus } = useHealth()

  const navigation = [
    { name: 'Chat', href: '/chat', icon: MessageSquare },
    { name: 'OCR', href: '/ocr', icon: FileText },
    { name: 'Providers', href: '/providers', icon: Server },
  ]

  const isActive = (path: string) => location.pathname === path

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-secondary-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-secondary-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-bold text-primary-600">Ageny Online</h1>
              <div className="ml-4 flex items-center">
                <Activity 
                  className={`w-4 h-4 mr-2 ${
                    healthStatus.status === 'healthy' 
                      ? 'text-green-500' 
                      : healthStatus.status === 'unhealthy' 
                      ? 'text-red-500' 
                      : 'text-yellow-500'
                  }`} 
                />
                <span className={`text-sm font-medium ${
                  healthStatus.status === 'healthy' 
                    ? 'text-green-700' 
                    : healthStatus.status === 'unhealthy' 
                    ? 'text-red-700' 
                    : 'text-yellow-700'
                }`}>
                  {healthStatus.status === 'healthy' ? 'Online' : 
                   healthStatus.status === 'unhealthy' ? 'Offline' : 'Checking...'}
                </span>
              </div>
            </div>
            
            {healthStatus.app && (
              <div className="text-sm text-secondary-500">
                v{healthStatus.app.version} • {healthStatus.app.environment}
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-white border-b border-secondary-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            {navigation.map((item) => {
              const Icon = item.icon
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`flex items-center px-3 py-4 text-sm font-medium border-b-2 transition-colors duration-200 ${
                    isActive(item.href)
                      ? 'border-primary-500 text-primary-600'
                      : 'border-transparent text-secondary-500 hover:text-secondary-700 hover:border-secondary-300'
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