import { createContext, useContext, ReactNode } from 'react'
import axios, { AxiosInstance } from 'axios'

interface ApiContextType {
  api: AxiosInstance
}

const ApiContext = createContext<ApiContextType | undefined>(undefined)

export function ApiProvider({ children }: { children: ReactNode }) {
  const api = axios.create({
    baseURL: '/api',
    timeout: 30000,
    headers: {
      'Content-Type': 'application/json',
    },
  })

  // Request interceptor
  api.interceptors.request.use(
    (config) => {
      console.log('API Request:', config.method?.toUpperCase(), config.url)
      return config
    },
    (error) => {
      console.error('API Request Error:', error)
      return Promise.reject(error)
    }
  )

  // Response interceptor
  api.interceptors.response.use(
    (response) => {
      console.log('API Response:', response.status, response.config.url)
      return response
    },
    (error) => {
      console.error('API Response Error:', error.response?.status, error.response?.data)
      return Promise.reject(error)
    }
  )

  return (
    <ApiContext.Provider value={{ api }}>
      {children}
    </ApiContext.Provider>
  )
}

export function useApi() {
  const context = useContext(ApiContext)
  if (context === undefined) {
    throw new Error('useApi must be used within an ApiProvider')
  }
  return context
} 