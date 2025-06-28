import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, FileText, Download, Trash2 } from 'lucide-react'
import { useApi } from '../contexts/ApiContext'
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
      toast.success(`Przetworzono ${acceptedFiles.length} plik(ów)`)
    } catch (error: any) {
      console.error('OCR error:', error)
      toast.error(error.response?.data?.detail || 'Błąd podczas przetwarzania OCR')
    } finally {
      setIsProcessing(false)
    }
  }, [api, selectedProvider])

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
    toast.success('Skopiowano do schowka')
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
    toast.success('Pobrano plik tekstowy')
  }

  const deleteResult = (id: string) => {
    setResults(prev => prev.filter(result => result.id !== id))
    toast.success('Usunięto wynik')
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Upload Section */}
      <div className="card">
        <h1 className="text-2xl font-bold text-secondary-900 mb-6">OCR - Rozpoznawanie Tekstu</h1>
        
        <div className="mb-6">
          <label className="block text-sm font-medium text-secondary-700 mb-2">
            Provider OCR (opcjonalny)
          </label>
          <select
            value={selectedProvider}
            onChange={(e) => setSelectedProvider(e.target.value)}
            className="input-field"
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
          className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors duration-200 ${
            isDragActive
              ? 'border-primary-400 bg-primary-50'
              : 'border-secondary-300 hover:border-primary-400 hover:bg-primary-50'
          } ${isProcessing ? 'opacity-50 cursor-not-allowed' : ''}`}
        >
          <input {...getInputProps()} />
          <Upload className="w-12 h-12 mx-auto mb-4 text-secondary-400" />
          {isProcessing ? (
            <p className="text-secondary-600">Przetwarzanie...</p>
          ) : isDragActive ? (
            <p className="text-primary-600">Upuść pliki tutaj...</p>
          ) : (
            <div>
              <p className="text-secondary-600 mb-2">
                Przeciągnij i upuść obrazy lub kliknij, aby wybrać
              </p>
              <p className="text-sm text-secondary-500">
                Obsługiwane formaty: JPEG, PNG, GIF, BMP, WebP
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Results */}
      {results.length > 0 && (
        <div className="card">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-secondary-900">Wyniki OCR</h2>
            <div className="text-sm text-secondary-500">
              {results.length} wynik(ów)
            </div>
          </div>

          <div className="space-y-4">
            {results.map((result) => (
              <div key={result.id} className="border border-secondary-200 rounded-lg p-4">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <span className="text-sm font-medium text-secondary-700">
                        Provider: {result.provider}
                      </span>
                      <span className="text-sm text-secondary-500">
                        • Model: {result.modelUsed}
                      </span>
                      <span className="text-sm text-secondary-500">
                        • Pewność: {(result.confidence * 100).toFixed(1)}%
                      </span>
                      {result.cost && (
                        <span className="text-sm text-secondary-500">
                          • Koszt: ${result.cost.toFixed(4)}
                        </span>
                      )}
                    </div>
                    <div className="text-xs text-secondary-500">
                      {result.timestamp.toLocaleString()}
                    </div>
                  </div>
                  <div className="flex space-x-2">
                    <button
                      onClick={() => copyToClipboard(result.text)}
                      className="p-2 text-secondary-600 hover:text-primary-600 transition-colors"
                      title="Kopiuj tekst"
                    >
                      <FileText className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => downloadText(result.text, `ocr-${result.id}`)}
                      className="p-2 text-secondary-600 hover:text-primary-600 transition-colors"
                      title="Pobierz jako plik"
                    >
                      <Download className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => deleteResult(result.id)}
                      className="p-2 text-secondary-600 hover:text-red-600 transition-colors"
                      title="Usuń wynik"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
                
                <div className="bg-secondary-50 rounded-lg p-3">
                  <div className="text-secondary-900 whitespace-pre-wrap text-sm">
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