import { useState, useEffect } from 'react'
import { Server, CheckCircle, XCircle, AlertCircle, RefreshCw } from 'lucide-react'
import { useApi } from '../contexts/ApiContext'
import { useHealth } from '../contexts/HealthContext'
import toast from 'react-hot-toast'

interface Provider {
  name: string
  status: 'healthy' | 'unhealthy' | 'unknown'
  details?: any
}

export default function ProvidersPage() {
  const { api } = useApi()
  const { healthStatus, refreshHealth, isLoading } = useHealth()
  const [providers, setProviders] = useState<Provider[]>([])
  const [models, setModels] = useState<any>({})

  useEffect(() => {
    if (healthStatus.providers) {
      const providerList = Object.entries(healthStatus.providers).map(([name, details]) => ({
        name,
        status: details?.status || 'unknown',
        details,
      }))
      setProviders(providerList)
    }
  }, [healthStatus.providers])

  const fetchModels = async () => {
    try {
      const response = await api.get('/v2/chat/models')
      setModels(response.data.models || {})
    } catch (error) {
      console.error('Failed to fetch models:', error)
    }
  }

  useEffect(() => {
    fetchModels()
  }, [])

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
        return <CheckCircle className="w-5 h-5 text-green-500" />
      case 'unhealthy':
        return <XCircle className="w-5 h-5 text-red-500" />
      default:
        return <AlertCircle className="w-5 h-5 text-yellow-500" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
        return 'text-green-700 bg-green-50 border-green-200'
      case 'unhealthy':
        return 'text-red-700 bg-red-50 border-red-200'
      default:
        return 'text-yellow-700 bg-yellow-50 border-yellow-200'
    }
  }

  const handleRefresh = async () => {
    await refreshHealth()
    await fetchModels()
    toast.success('Odświeżono status providerów')
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Health Status */}
      <div className="card">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-bold text-secondary-900">Status Providerów</h1>
          <button
            onClick={handleRefresh}
            disabled={isLoading}
            className="btn-secondary flex items-center space-x-2"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
            <span>Odśwież</span>
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {providers.map((provider) => (
            <div
              key={provider.name}
              className={`p-4 rounded-lg border ${getStatusColor(provider.status)}`}
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center space-x-2">
                  <Server className="w-5 h-5" />
                  <span className="font-medium capitalize">
                    {provider.name.replace('_', ' ')}
                  </span>
                </div>
                {getStatusIcon(provider.status)}
              </div>
              
              <div className="text-sm">
                <div className="mb-1">
                  Status: <span className="font-medium capitalize">{provider.status}</span>
                </div>
                {provider.details?.provider && (
                  <div className="mb-1">
                    Provider: <span className="font-medium">{provider.details.provider}</span>
                  </div>
                )}
                {provider.details?.model && (
                  <div className="mb-1">
                    Model: <span className="font-medium">{provider.details.model}</span>
                  </div>
                )}
                {provider.details?.error && (
                  <div className="text-red-600 text-xs mt-2">
                    Błąd: {provider.details.error}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Available Models */}
      <div className="card">
        <h2 className="text-xl font-semibold text-secondary-900 mb-6">Dostępne Modele</h2>
        
        <div className="space-y-4">
          {Object.entries(models).map(([provider, modelList]) => (
            <div key={provider} className="border border-secondary-200 rounded-lg p-4">
              <h3 className="font-medium text-secondary-900 mb-3 capitalize">
                {provider.replace('_', ' ')} Models
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2">
                {Array.isArray(modelList) && modelList.map((model: string, index: number) => (
                  <div
                    key={index}
                    className="text-sm text-secondary-600 bg-secondary-50 px-3 py-2 rounded"
                  >
                    {model}
                  </div>
                ))}
                {(!Array.isArray(modelList) || modelList.length === 0) && (
                  <div className="text-sm text-secondary-500 italic">
                    Brak dostępnych modeli
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* System Information */}
      {healthStatus.app && (
        <div className="card">
          <h2 className="text-xl font-semibold text-secondary-900 mb-6">Informacje Systemowe</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center p-4 bg-secondary-50 rounded-lg">
              <div className="text-2xl font-bold text-primary-600">{healthStatus.app.name}</div>
              <div className="text-sm text-secondary-600">Nazwa Aplikacji</div>
            </div>
            
            <div className="text-center p-4 bg-secondary-50 rounded-lg">
              <div className="text-2xl font-bold text-primary-600">v{healthStatus.app.version}</div>
              <div className="text-sm text-secondary-600">Wersja</div>
            </div>
            
            <div className="text-center p-4 bg-secondary-50 rounded-lg">
              <div className="text-2xl font-bold text-primary-600 capitalize">{healthStatus.app.environment}</div>
              <div className="text-sm text-secondary-600">Środowisko</div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
} 