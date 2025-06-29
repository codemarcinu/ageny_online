import { useState, useRef, useEffect } from 'react'
import { Send, Bot, User, Loader2, Globe, ExternalLink, Sparkles } from 'lucide-react'
import { useApi } from '../contexts/ApiContext'
import { useGamification } from '../contexts/GamificationContext'
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
  const { addPoints, unlockAchievement, updateChallengeProgress } = useGamification()
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
      const response = await api.post('/api/v2/chat/chat', {
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
      
      // Gamification rewards
      const newMessageCount = messages.length + 2 // +2 for user and assistant messages
      addPoints(10)
      
      // Check for first chat achievement
      if (newMessageCount === 2) {
        unlockAchievement('first-chat')
        toast.success('🎉 Osiągnięcie odblokowane: Pierwszy krok!')
      }
      
      // Check for chat master achievement
      if (newMessageCount >= 20) {
        unlockAchievement('chat-master')
        toast.success('👑 Osiągnięcie odblokowane: Mistrz rozmów!')
      }
      
      // Update daily challenge progress
      updateChallengeProgress('daily-chat-3', Math.ceil(newMessageCount / 2))
      
      if (response.data.web_search_used) {
        toast.success('✨ Odpowiedź z aktualnymi informacjami z internetu!')
      } else {
        toast.success('💬 Odpowiedź otrzymana!')
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
      <div className="mt-4 p-3 bg-teen-mint-50 border border-teen-mint-200 rounded-lg">
        <div className="flex items-center mb-2">
          <Globe className="w-4 h-4 text-teen-mint-600 mr-2" />
          <span className="text-sm font-medium text-teen-mint-800">Informacje z internetu:</span>
        </div>
        <div className="space-y-2">
          {results.map((result, index) => (
            <div key={index} className="text-sm">
              <div className="font-medium text-teen-mint-900 mb-1">
                {result.title}
              </div>
              <div className="text-teen-mint-700 mb-1">
                {result.snippet}
              </div>
              <div className="flex items-center text-xs text-teen-mint-600">
                <span className="mr-2">Źródło: {result.source}</span>
                <a 
                  href={result.url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="flex items-center hover:text-teen-mint-800"
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
      <div className="bg-white rounded-xl shadow-sm border border-teen-purple-200 p-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-gradient-to-r from-teen-pink-100 to-teen-purple-100 rounded-lg">
              <Sparkles className="w-6 h-6 text-teen-purple-600" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-teen-purple-700">Chat z AI</h1>
              <p className="text-sm text-teen-purple-600">Twój osobisty asystent gotowy do pomocy!</p>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <label className="flex items-center space-x-2 text-sm">
              <input
                type="checkbox"
                checked={enableWebSearch}
                onChange={(e) => setEnableWebSearch(e.target.checked)}
                className="rounded border-teen-purple-300 text-teen-purple-600 focus:ring-teen-purple-500"
              />
              <span className="text-teen-purple-700">Wyszukiwanie w internecie</span>
            </label>
            <div className="text-sm text-teen-purple-500 bg-teen-purple-50 px-3 py-1 rounded-full">
              {messages.length} wiadomości
            </div>
          </div>
        </div>

        {/* Messages */}
        <div className="h-96 overflow-y-auto mb-6 p-4 bg-gradient-to-br from-teen-pink-25 to-teen-purple-25 rounded-lg border border-teen-purple-100">
          {messages.length === 0 ? (
            <div className="text-center text-teen-purple-500 py-8">
              <Bot className="w-12 h-12 mx-auto mb-4 text-teen-purple-400" />
              <p className="text-lg font-medium mb-2">Rozpocznij rozmowę z AI asystentem! 💬</p>
              <p className="text-sm">Możesz pytać o wszystko - od zadań domowych po ciekawe fakty!</p>
              {enableWebSearch && (
                <p className="text-xs mt-3 text-teen-purple-400 bg-teen-purple-50 px-3 py-2 rounded-lg">
                  🌐 Wyszukiwanie w internecie jest włączone - AI będzie mogło korzystać z aktualnych informacji
                </p>
              )}
            </div>
          ) : (
            messages.map((message) => (
              <div
                key={message.id}
                className={`mb-4 ${message.role === 'user' ? 'text-right' : 'text-left'}`}
              >
                <div className={`inline-flex items-start max-w-xs lg:max-w-md ${
                  message.role === 'user' ? 'flex-row-reverse' : 'flex-row'
                }`}>
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center mr-3 ${
                    message.role === 'user' 
                      ? 'bg-gradient-to-r from-teen-pink-400 to-teen-pink-600 text-white' 
                      : 'bg-gradient-to-r from-teen-purple-400 to-teen-purple-600 text-white'
                  }`}>
                    {message.role === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
                  </div>
                  <div className={`flex-1 ${
                    message.role === 'user' ? 'mr-3' : 'ml-3'
                  }`}>
                    <div className={`p-3 rounded-lg ${
                      message.role === 'user'
                        ? 'bg-gradient-to-r from-teen-pink-400 to-teen-pink-600 text-white'
                        : 'bg-white border border-teen-purple-200 text-teen-purple-700'
                    }`}>
                      <div className="text-sm font-medium mb-1">
                        {message.role === 'user' ? 'Ty' : 'AI Asystent'}
                        {message.webSearchUsed && (
                          <span className="ml-2 inline-flex items-center text-xs opacity-80">
                            <Globe className="w-3 h-3 mr-1" />
                            z internetu
                          </span>
                        )}
                      </div>
                      <div className="whitespace-pre-wrap">
                        {message.content}
                      </div>
                      {message.webSearchResults && message.webSearchResults.length > 0 && (
                        renderWebSearchResults(message.webSearchResults)
                      )}
                    </div>
                    <div className="text-xs text-teen-purple-500 mt-1">
                      {message.timestamp.toLocaleTimeString()}
                    </div>
                  </div>
                </div>
              </div>
            ))
          )}
          
          {isLoading && (
            <div className="text-left">
              <div className="inline-flex items-start">
                <div className="w-8 h-8 rounded-full bg-gradient-to-r from-teen-purple-400 to-teen-purple-600 text-white flex items-center justify-center mr-3">
                  <Bot className="w-4 h-4" />
                </div>
                <div className="bg-white border border-teen-purple-200 rounded-lg p-3">
                  <div className="flex items-center space-x-2">
                    <Loader2 className="w-4 h-4 animate-spin text-teen-purple-600" />
                    <span className="text-teen-purple-600">AI myśli...</span>
                  </div>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="flex space-x-4">
          <div className="flex-1">
            <textarea
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Napisz wiadomość..."
              className="w-full p-3 border border-teen-purple-200 rounded-lg focus:ring-2 focus:ring-teen-purple-500 focus:border-transparent resize-none"
              rows={3}
              disabled={isLoading}
            />
          </div>
          <button
            onClick={sendMessage}
            disabled={!inputMessage.trim() || isLoading}
            className="px-6 py-3 bg-gradient-to-r from-teen-pink-500 to-teen-purple-600 text-white rounded-lg hover:from-teen-pink-600 hover:to-teen-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center space-x-2"
          >
            {isLoading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Send className="w-4 h-4" />
            )}
            <span>Wyślij</span>
          </button>
        </div>
      </div>
    </div>
  )
} 