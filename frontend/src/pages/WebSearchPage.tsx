import { useState } from 'react'
import { Search, Globe, ExternalLink, Loader2, Info } from 'lucide-react'
import { useApi } from '../contexts/ApiContext'
import toast from 'react-hot-toast'

interface SearchResult {
  title: string
  url: string
  snippet: string
  source: string
  timestamp: string
}

interface SearchResponse {
  query: string
  results: SearchResult[]
  total_results: number
  search_engine: string
  search_time: number
}

export default function WebSearchPage() {
  const { api } = useApi()
  const [query, setQuery] = useState('')
  const [searchResults, setSearchResults] = useState<SearchResponse | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [searchEngine, setSearchEngine] = useState('duckduckgo')

  const performSearch = async () => {
    if (!query.trim() || isLoading) return

    setIsLoading(true)
    try {
      const response = await api.post('/v2/web-search/search', {
        query: query.trim(),
        max_results: 5,
        search_engine: searchEngine
      })

      setSearchResults(response.data)
      toast.success(`Znaleziono ${response.data.total_results} wyników w ${response.data.search_time.toFixed(2)}s`)
    } catch (error: any) {
      console.error('Search error:', error)
      toast.error(error.response?.data?.detail || 'Błąd podczas wyszukiwania')
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault()
      performSearch()
    }
  }

  const testQueries = [
    'aktualne wiadomości',
    'pogoda Warszawa',
    'kurs dolara',
    'najnowsze technologie AI',
    'wydarzenia kulturalne w Polsce'
  ]

  const handleTestQuery = (testQuery: string) => {
    setQuery(testQuery)
  }

  return (
    <div className="max-w-6xl mx-auto">
      <div className="card">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-secondary-900">Wyszukiwanie w Internecie</h1>
            <p className="text-secondary-600 mt-1">
              Testuj funkcjonalność wyszukiwania aktualnych informacji
            </p>
          </div>
          <div className="flex items-center space-x-2 text-blue-600">
            <Globe className="w-5 h-5" />
            <span className="text-sm font-medium">Live Search</span>
          </div>
        </div>

        {/* Search Input */}
        <div className="mb-6">
          <div className="flex space-x-4 mb-4">
            <div className="flex-1">
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Wpisz zapytanie wyszukiwania..."
                className="input-field w-full"
                disabled={isLoading}
              />
            </div>
            <select
              value={searchEngine}
              onChange={(e) => setSearchEngine(e.target.value)}
              className="input-field"
              disabled={isLoading}
            >
              <option value="duckduckgo">DuckDuckGo</option>
            </select>
            <button
              onClick={performSearch}
              disabled={!query.trim() || isLoading}
              className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Search className="w-4 h-4" />
              )}
              <span className="ml-2">Szukaj</span>
            </button>
          </div>

          {/* Test Queries */}
          <div className="mb-4">
            <p className="text-sm text-secondary-600 mb-2">Przykładowe zapytania:</p>
            <div className="flex flex-wrap gap-2">
              {testQueries.map((testQuery, index) => (
                <button
                  key={index}
                  onClick={() => handleTestQuery(testQuery)}
                  className="px-3 py-1 text-xs bg-secondary-100 text-secondary-700 rounded-full hover:bg-secondary-200 transition-colors"
                >
                  {testQuery}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Results */}
        {searchResults && (
          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <div>
                <h3 className="font-medium text-blue-900">
                  Wyniki dla: "{searchResults.query}"
                </h3>
                <p className="text-sm text-blue-700">
                  Znaleziono {searchResults.total_results} wyników w {searchResults.search_time.toFixed(2)}s
                </p>
              </div>
              <div className="text-sm text-blue-600">
                Silnik: {searchResults.search_engine}
              </div>
            </div>

            <div className="space-y-4">
              {searchResults.results.map((result, index) => (
                <div key={index} className="p-4 border border-secondary-200 rounded-lg hover:bg-secondary-50 transition-colors">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h4 className="font-medium text-secondary-900 mb-2">
                        {result.title}
                      </h4>
                      <p className="text-secondary-700 text-sm mb-3">
                        {result.snippet}
                      </p>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4 text-xs text-secondary-500">
                          <span>Źródło: {result.source}</span>
                          <span>•</span>
                          <span>{new Date(result.timestamp).toLocaleString()}</span>
                        </div>
                        <a
                          href={result.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex items-center text-xs text-blue-600 hover:text-blue-800"
                        >
                          <ExternalLink className="w-3 h-3 mr-1" />
                          Otwórz
                        </a>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Info Section */}
        <div className="mt-8 p-4 bg-secondary-50 border border-secondary-200 rounded-lg">
          <div className="flex items-start">
            <Info className="w-5 h-5 text-secondary-600 mr-3 mt-0.5" />
            <div>
              <h3 className="font-medium text-secondary-900 mb-2">
                Jak działa wyszukiwanie w internecie?
              </h3>
              <ul className="text-sm text-secondary-700 space-y-1">
                <li>• Wyszukiwanie jest automatycznie aktywowane dla zapytań o aktualne informacje</li>
                <li>• AI może korzystać z wyników wyszukiwania, aby udzielić aktualnych odpowiedzi</li>
                <li>• Wszystkie źródła są weryfikowane i podane w odpowiedzi</li>
                <li>• Funkcja jest dostępna w trybie czatu z AI</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
} 