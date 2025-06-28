import { useState, useRef, useEffect } from 'react'
import { Send, Bot, User, Loader2, Globe, ExternalLink } from 'lucide-react'
import { useApi } from '../contexts/ApiContext'
import toast from 'react-hot-toast'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  webSearchUsed?: boolean
  webSearchResults?: Array<{
    title: string
    url: string
    snippet: string
    source: string
  }>
}

export default function ChatPage() {
  const { api } = useApi()
  const [messages, setMessages] = useState<Message[]>([])
  const [inputMessage, setInputMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [enableWebSearch, setEnableWebSearch] = useState(true)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: inputMessage,
      timestamp: new Date(),
    }

    setMessages(prev => [...prev, userMessage])
    setInputMessage('')
    setIsLoading(true)

    try {
      const response = await api.post('/v2/chat/completion', {
        messages: [
          ...messages.map(msg => ({ role: msg.role, content: msg.content })),
          { role: 'user', content: inputMessage }
        ],
        temperature: 0.7,
        max_tokens: 1000,
        enable_web_search: enableWebSearch,
      })

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.data.text,
        timestamp: new Date(),
        webSearchUsed: response.data.web_search_used,
        webSearchResults: response.data.web_search_results,
      }

      setMessages(prev => [...prev, assistantMessage])
      
      if (response.data.web_search_used) {
        toast.success('Odpowiedź z aktualnymi informacjami z internetu!')
      } else {
        toast.success('Odpowiedź otrzymana!')
      }
    } catch (error: any) {
      console.error('Chat error:', error)
      toast.error(error.response?.data?.detail || 'Błąd podczas wysyłania wiadomości')
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const renderWebSearchResults = (results: Array<{title: string, url: string, snippet: string, source: string}>) => {
    return (
      <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
        <div className="flex items-center mb-2">
          <Globe className="w-4 h-4 text-blue-600 mr-2" />
          <span className="text-sm font-medium text-blue-800">Informacje z internetu:</span>
        </div>
        <div className="space-y-2">
          {results.map((result, index) => (
            <div key={index} className="text-sm">
              <div className="font-medium text-blue-900 mb-1">
                {result.title}
              </div>
              <div className="text-blue-700 mb-1">
                {result.snippet}
              </div>
              <div className="flex items-center text-xs text-blue-600">
                <span className="mr-2">Źródło: {result.source}</span>
                <a 
                  href={result.url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="flex items-center hover:text-blue-800"
                >
                  <ExternalLink className="w-3 h-3 mr-1" />
                  Otwórz
                </a>
              </div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="card">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-bold text-secondary-900">Chat z AI</h1>
          <div className="flex items-center space-x-4">
            <label className="flex items-center space-x-2 text-sm">
              <input
                type="checkbox"
                checked={enableWebSearch}
                onChange={(e) => setEnableWebSearch(e.target.checked)}
                className="rounded border-secondary-300 text-primary-600 focus:ring-primary-500"
              />
              <span className="text-secondary-700">Wyszukiwanie w internecie</span>
            </label>
            <div className="text-sm text-secondary-500">
              {messages.length} wiadomości
            </div>
          </div>
        </div>

        {/* Messages */}
        <div className="h-96 overflow-y-auto mb-6 p-4 bg-secondary-50 rounded-lg">
          {messages.length === 0 ? (
            <div className="text-center text-secondary-500 py-8">
              <Bot className="w-12 h-12 mx-auto mb-4 text-secondary-400" />
              <p>Rozpocznij rozmowę z AI asystentem</p>
              {enableWebSearch && (
                <p className="text-xs mt-2 text-secondary-400">
                  Wyszukiwanie w internecie jest włączone - AI będzie mogło korzystać z aktualnych informacji
                </p>
              )}
            </div>
          ) : (
            messages.map((message) => (
              <div
                key={message.id}
                className={`chat-message ${message.role}`}
              >
                <div className="flex items-start">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center mr-3 ${
                    message.role === 'user' 
                      ? 'bg-primary-100 text-primary-600' 
                      : 'bg-secondary-100 text-secondary-600'
                  }`}>
                    {message.role === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
                  </div>
                  <div className="flex-1">
                    <div className="text-sm font-medium text-secondary-700 mb-1">
                      {message.role === 'user' ? 'Ty' : 'AI Asystent'}
                      {message.webSearchUsed && (
                        <span className="ml-2 inline-flex items-center text-xs text-blue-600">
                          <Globe className="w-3 h-3 mr-1" />
                          z internetu
                        </span>
                      )}
                    </div>
                    <div className="text-secondary-900 whitespace-pre-wrap">
                      {message.content}
                    </div>
                    {message.webSearchResults && message.webSearchResults.length > 0 && (
                      renderWebSearchResults(message.webSearchResults)
                    )}
                    <div className="text-xs text-secondary-500 mt-2">
                      {message.timestamp.toLocaleTimeString()}
                    </div>
                  </div>
                </div>
              </div>
            ))
          )}
          
          {isLoading && (
            <div className="chat-message assistant">
              <div className="flex items-start">
                <div className="w-8 h-8 rounded-full bg-secondary-100 text-secondary-600 flex items-center justify-center mr-3">
                  <Bot className="w-4 h-4" />
                </div>
                <div className="flex-1">
                  <div className="text-sm font-medium text-secondary-700 mb-1">
                    AI Asystent
                  </div>
                  <div className="flex items-center text-secondary-600">
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    {enableWebSearch ? 'Wyszukuję informacje i piszę odpowiedź...' : 'Piszę odpowiedź...'}
                  </div>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="flex space-x-4">
          <textarea
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Napisz wiadomość..."
            className="input-field flex-1 resize-none"
            rows={3}
            disabled={isLoading}
          />
          <button
            onClick={sendMessage}
            disabled={!inputMessage.trim() || isLoading}
            className="btn-primary self-end disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  )
} 