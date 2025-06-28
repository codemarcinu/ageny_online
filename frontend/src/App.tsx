import { Routes, Route } from 'react-router-dom'
import { useState, useEffect } from 'react'
import Layout from './components/Layout'
import ChatPage from './pages/ChatPage'
import OCRPage from './pages/OCRPage'
import ProvidersPage from './pages/ProvidersPage'
import { ApiProvider } from './contexts/ApiContext'
import { HealthProvider } from './contexts/HealthContext'

function App() {
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
      <div className="min-h-screen bg-gradient-to-br from-primary-50 to-secondary-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <h2 className="text-xl font-semibold text-secondary-700">Ładowanie Ageny Online...</h2>
        </div>
      </div>
    )
  }

  return (
    <ApiProvider>
      <HealthProvider>
        <Layout>
          <Routes>
            <Route path="/" element={<ChatPage />} />
            <Route path="/chat" element={<ChatPage />} />
            <Route path="/ocr" element={<OCRPage />} />
            <Route path="/providers" element={<ProvidersPage />} />
          </Routes>
        </Layout>
      </HealthProvider>
    </ApiProvider>
  )
}

export default App 