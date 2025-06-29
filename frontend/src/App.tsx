import { Routes, Route } from 'react-router-dom'
import { useState, useEffect } from 'react'
import Layout from './components/Layout'
import ChatPage from './pages/ChatPage'
import OCRPage from './pages/OCRPage'
import ProvidersPage from './pages/ProvidersPage'
import WebSearchPage from './pages/WebSearchPage'
import TeenDashboard from './pages/TeenDashboard'
import CookingPage from './pages/CookingPage'
import ConfettiAnimation from './components/gamification/ConfettiAnimation'
import { ApiProvider } from './contexts/ApiContext'
import { HealthProvider } from './contexts/HealthContext'
import { GamificationProvider, useGamification } from './contexts/GamificationContext'

function AppContent() {
  const { showConfetti } = useGamification()
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Simulate initial loading
    const timer = setTimeout(() => {
      setIsLoading(false)
    }, 1000)

    return () => clearTimeout(timer)
  }, [])

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-teen-pink-50 to-teen-purple-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teen-purple-600 mx-auto mb-4"></div>
          <h2 className="text-xl font-semibold text-teen-purple-700">Ładowanie Ageny Online...</h2>
        </div>
      </div>
    )
  }

  return (
    <>
      <Layout>
        <Routes>
          <Route path="/" element={<TeenDashboard />} />
          <Route path="/dashboard" element={<TeenDashboard />} />
          <Route path="/chat" element={<ChatPage />} />
          <Route path="/ocr" element={<OCRPage />} />
          <Route path="/providers" element={<ProvidersPage />} />
          <Route path="/web-search" element={<WebSearchPage />} />
          <Route path="/cooking" element={<CookingPage />} />
        </Routes>
      </Layout>
      <ConfettiAnimation isVisible={showConfetti} />
    </>
  )
}

function App() {
  return (
    <GamificationProvider>
      <ApiProvider>
        <HealthProvider>
          <AppContent />
        </HealthProvider>
      </ApiProvider>
    </GamificationProvider>
  )
}

export default App 