import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, FileText, Download, Trash2, Camera, Sparkles } from 'lucide-react'
import { useApi } from '../contexts/ApiContext'
import { useGamification } from '../contexts/GamificationContext'
import toast from 'react-hot-toast'

interface OCRResult {
  id: string
  text: string
  confidence: number
  provider: string
  modelUsed: string
  cost?: number
  tokensUsed?: number
  metadata: any
  timestamp: Date
}

export default function OCRPage() {
  const { api } = useApi()
  const { addPoints, unlockAchievement, updateChallengeProgress } = useGamification()
  const [results, setResults] = useState<OCRResult[]>([])
  const [isProcessing, setIsProcessing] = useState(false)
  const [selectedProvider, setSelectedProvider] = useState<string>('')

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return

    setIsProcessing(true)
    const newResults: OCRResult[] = []

    try {
      for (const file of acceptedFiles) {
        const formData = new FormData()
        formData.append('file', file)
        
        if (selectedProvider) {
          formData.append('provider', selectedProvider)
        }

        const response = await api.post('/v2/ocr/extract-text', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        })

        const result: OCRResult = {
          id: Date.now().toString() + Math.random(),
          text: response.data.text,
          confidence: response.data.confidence,
          provider: response.data.provider,
          modelUsed: response.data.model_used,
          cost: response.data.cost,
          tokensUsed: response.data.tokens_used,
          metadata: response.data.metadata,
          timestamp: new Date(),
        }

        newResults.push(result)
      }

      setResults(prev => [...newResults, ...prev])
      
      // Gamification rewards
      addPoints(25)
      
      // Check for first OCR achievement
      if (results.length === 0) {
        unlockAchievement('ocr-explorer')
        toast.success('📷 Osiągnięcie odblokowane: Eksplorator dokumentów!')
      }
      
      // Update daily challenge progress
      updateChallengeProgress('daily-ocr-1', results.length + newResults.length)
      
      toast.success(`✨ Przetworzono ${acceptedFiles.length} plik(ów)!`)
    } catch (error: any) {
      console.error('OCR error:', error)
      toast.error(error.response?.data?.detail || 'Błąd podczas przetwarzania OCR')
    } finally {
      setIsProcessing(false)
    }
  }, [api, selectedProvider, results.length, addPoints, unlockAchievement, updateChallengeProgress])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.gif', '.bmp', '.webp']
    },
    multiple: true,
    disabled: isProcessing,
  })

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
    toast.success('📋 Skopiowano do schowka!')
  }

  const downloadText = (text: string, filename: string) => {
    const blob = new Blob([text], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${filename}.txt`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
    toast.success('💾 Pobrano plik tekstowy!')
  }

  const deleteResult = (id: string) => {
    setResults(prev => prev.filter(result => result.id !== id))
    toast.success('🗑️ Usunięto wynik!')
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Upload Section */}
      <div className="bg-white rounded-xl shadow-sm border border-teen-purple-200 p-6">
        <div className="flex items-center space-x-3 mb-6">
          <div className="p-2 bg-gradient-to-r from-teen-mint-100 to-teen-purple-100 rounded-lg">
            <Camera className="w-6 h-6 text-teen-mint-600" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-teen-purple-700">Skanowanie dokumentów</h1>
            <p className="text-sm text-teen-purple-600">Przeskanuj obrazy i wyciągnij z nich tekst!</p>
          </div>
        </div>
        
        <div className="mb-6">
          <label className="block text-sm font-medium text-teen-purple-700 mb-2">
            Provider OCR (opcjonalny)
          </label>
          <select
            value={selectedProvider}
            onChange={(e) => setSelectedProvider(e.target.value)}
            className="w-full p-3 border border-teen-purple-200 rounded-lg focus:ring-2 focus:ring-teen-purple-500 focus:border-transparent"
            disabled={isProcessing}
          >
            <option value="">Automatyczny wybór</option>
            <option value="mistral_vision">Mistral Vision</option>
            <option value="azure_vision">Azure Vision</option>
            <option value="google_vision">Google Vision</option>
          </select>
        </div>

        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-all duration-200 ${
            isDragActive
              ? 'border-teen-mint-400 bg-teen-mint-50'
              : 'border-teen-purple-300 hover:border-teen-mint-400 hover:bg-teen-mint-50'
          } ${isProcessing ? 'opacity-50 cursor-not-allowed' : ''}`}
        >
          <input {...getInputProps()} />
          <Upload className="w-12 h-12 mx-auto mb-4 text-teen-purple-400" />
          {isProcessing ? (
            <div className="flex items-center justify-center space-x-2">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-teen-mint-600"></div>
              <p className="text-teen-purple-600">Przetwarzanie...</p>
            </div>
          ) : isDragActive ? (
            <p className="text-teen-mint-600 font-medium">Upuść pliki tutaj...</p>
          ) : (
            <div>
              <p className="text-teen-purple-600 mb-2 font-medium">
                Przeciągnij i upuść obrazy lub kliknij, aby wybrać
              </p>
              <p className="text-sm text-teen-purple-500">
                Obsługiwane formaty: JPEG, PNG, GIF, BMP, WebP
              </p>
              <div className="mt-4 flex items-center justify-center space-x-2 text-xs text-teen-purple-400">
                <Sparkles className="w-3 h-3" />
                <span>Dostępne dla zadań domowych i notatek!</span>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Results */}
      {results.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm border border-teen-purple-200 p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-teen-purple-700">Wyniki skanowania</h2>
            <div className="text-sm text-teen-purple-500 bg-teen-purple-50 px-3 py-1 rounded-full">
              {results.length} wynik(ów)
            </div>
          </div>

          <div className="space-y-4">
            {results.map((result) => (
              <div key={result.id} className="border border-teen-purple-200 rounded-lg p-4 hover:bg-teen-purple-25 transition-colors">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2 flex-wrap">
                      <span className="text-sm font-medium text-teen-purple-700 bg-teen-purple-100 px-2 py-1 rounded">
                        {result.provider}
                      </span>
                      <span className="text-sm text-teen-purple-500">
                        Model: {result.modelUsed}
                      </span>
                      <span className="text-sm text-teen-purple-500">
                        Pewność: {(result.confidence * 100).toFixed(1)}%
                      </span>
                      {result.cost && (
                        <span className="text-sm text-teen-purple-500">
                          Koszt: ${result.cost.toFixed(4)}
                        </span>
                      )}
                    </div>
                    <div className="text-xs text-teen-purple-500">
                      {result.timestamp.toLocaleString()}
                    </div>
                  </div>
                  <div className="flex space-x-2">
                    <button
                      onClick={() => copyToClipboard(result.text)}
                      className="p-2 text-teen-purple-600 hover:text-teen-mint-600 hover:bg-teen-mint-50 rounded transition-colors"
                      title="Kopiuj tekst"
                    >
                      <FileText className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => downloadText(result.text, `ocr-${result.id}`)}
                      className="p-2 text-teen-purple-600 hover:text-teen-mint-600 hover:bg-teen-mint-50 rounded transition-colors"
                      title="Pobierz jako plik"
                    >
                      <Download className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => deleteResult(result.id)}
                      className="p-2 text-teen-purple-600 hover:text-red-600 hover:bg-red-50 rounded transition-colors"
                      title="Usuń wynik"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
                <div className="bg-teen-purple-50 rounded-lg p-3">
                  <div className="text-sm text-teen-purple-700 whitespace-pre-wrap">
                    {result.text}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
} 