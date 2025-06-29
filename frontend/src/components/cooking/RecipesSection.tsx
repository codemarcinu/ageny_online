import { useState, useEffect } from 'react'
import { Search, BookOpen, Clock, Users, Star, Trash2, Sparkles } from 'lucide-react'
import { useApi } from '../../contexts/ApiContext'
import { useGamification } from '../../contexts/GamificationContext'
import toast from 'react-hot-toast'

interface Recipe {
  id: number
  name: string
  description?: string
  ingredients: Array<{
    name: string
    amount: string
    unit: string
  }>
  instructions: string
  cooking_time?: number
  difficulty?: string
  servings?: number
  calories_per_serving?: number
  tags?: string[]
  is_ai_generated: boolean
  created_at: string
  updated_at: string
}

interface GenerateRecipeForm {
  ingredients: string[]
  preferences: string
}

export default function RecipesSection() {
  const [recipes, setRecipes] = useState<Recipe[]>([])
  const [loading, setLoading] = useState(true)
  const [showGenerateForm, setShowGenerateForm] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [generatedRecipe, setGeneratedRecipe] = useState<Recipe | null>(null)
  const [generating, setGenerating] = useState(false)
  
  const { api } = useApi()
  const { addPoints, unlockAchievement, checkCookingEnthusiast } = useGamification()

  const [generateForm, setGenerateForm] = useState<GenerateRecipeForm>({
    ingredients: [''],
    preferences: ''
  })

  useEffect(() => {
    fetchRecipes()
  }, [])

  const fetchRecipes = async () => {
    try {
      setLoading(true)
      const response = await api.get('/v2/cooking/recipes/list')
      setRecipes(response.data.recipes || [])
    } catch (error) {
      console.error('Błąd podczas pobierania przepisów:', error)
      toast.error('Nie udało się pobrać przepisów')
    } finally {
      setLoading(false)
    }
  }

  const handleGenerateRecipe = async (e: React.FormEvent) => {
    e.preventDefault()
    
    try {
      setGenerating(true)
      const response = await api.post('/v2/cooking/recipes/generate', {
        ingredients: generateForm.ingredients.filter(i => i.trim()),
        preferences: generateForm.preferences
      }, {
        params: { user_id: 1 }
      })
      
      setGeneratedRecipe(response.data.recipe)
      addPoints(10)
      
      // Sprawdź osiągnięcia
      const newRecipeCount = recipes.length + 1
      if (newRecipeCount === 1) {
        unlockAchievement('first-recipe')
        checkCookingEnthusiast()
      }
      if (newRecipeCount === 5) {
        unlockAchievement('recipe-master')
      }
      
      toast.success('Przepis został wygenerowany!')
    } catch (error) {
      console.error('Błąd podczas generowania przepisu:', error)
      toast.error('Nie udało się wygenerować przepisu')
    } finally {
      setGenerating(false)
    }
  }

  const handleDeleteRecipe = async (recipeId: number) => {
    if (!confirm('Czy na pewno chcesz usunąć ten przepis?')) return
    
    try {
      await api.delete(`/v2/cooking/recipes/${recipeId}`)
      toast.success('Przepis został usunięty')
      addPoints(2)
      fetchRecipes()
    } catch (error) {
      console.error('Błąd podczas usuwania przepisu:', error)
      toast.error('Nie udało się usunąć przepisu')
    }
  }

  const resetGenerateForm = () => {
    setGenerateForm({
      ingredients: [''],
      preferences: ''
    })
  }

  const addIngredient = () => {
    setGenerateForm({
      ...generateForm,
      ingredients: [...generateForm.ingredients, '']
    })
  }

  const removeIngredient = (index: number) => {
    setGenerateForm({
      ...generateForm,
      ingredients: generateForm.ingredients.filter((_, i) => i !== index)
    })
  }

  const filteredRecipes = recipes.filter(recipe =>
    recipe.name.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const renderGenerateForm = () => (
    <div className="p-6 border-b border-teen-purple-200">
      <h3 className="text-lg font-semibold text-teen-purple-700 mb-4 flex items-center">
        <Sparkles className="w-5 h-5 mr-2 text-teen-pink-500" />
        Generuj przepis AI
      </h3>
      
      <form onSubmit={handleGenerateRecipe} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-teen-purple-700 mb-2">
            Dostępne składniki
          </label>
          {generateForm.ingredients.map((ingredient, index) => (
            <div key={index} className="flex gap-2 mb-2">
              <input
                type="text"
                value={ingredient}
                onChange={(e) => {
                  const newIngredients = [...generateForm.ingredients]
                  newIngredients[index] = e.target.value
                  setGenerateForm({ ...generateForm, ingredients: newIngredients })
                }}
                placeholder="np. pomidor, cebula, oliwa"
                className="flex-1 px-3 py-2 border border-teen-purple-300 rounded-lg focus:ring-2 focus:ring-teen-purple-500 focus:border-transparent"
              />
              {generateForm.ingredients.length > 1 && (
                <button
                  type="button"
                  onClick={() => removeIngredient(index)}
                  className="px-3 py-2 text-red-500 hover:text-red-700 hover:bg-red-100 rounded-lg"
                >
                  Usuń
                </button>
              )}
            </div>
          ))}
          <button
            type="button"
            onClick={addIngredient}
            className="text-teen-purple-600 hover:text-teen-purple-700 text-sm"
          >
            + Dodaj składnik
          </button>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-teen-purple-700 mb-1">
            Preferencje (opcjonalnie)
          </label>
          <textarea
            value={generateForm.preferences}
            onChange={(e) => setGenerateForm({...generateForm, preferences: e.target.value})}
            placeholder="np. wegetariańska kuchnia, szybkie danie, dla dzieci"
            className="w-full px-3 py-2 border border-teen-purple-300 rounded-lg focus:ring-2 focus:ring-teen-purple-500 focus:border-transparent"
            rows={3}
          />
        </div>
        
        <div className="flex space-x-3">
          <button
            type="submit"
            disabled={generating}
            className="flex items-center px-4 py-2 bg-gradient-to-r from-teen-pink-500 to-teen-purple-500 text-white rounded-lg hover:from-teen-pink-600 hover:to-teen-purple-600 transition-all duration-200 disabled:opacity-50"
          >
            {generating ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Generuję...
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4 mr-2" />
                Generuj przepis
              </>
            )}
          </button>
          <button
            type="button"
            onClick={() => {
              setShowGenerateForm(false)
              resetGenerateForm()
            }}
            className="px-4 py-2 border border-teen-purple-300 text-teen-purple-700 rounded-lg hover:bg-teen-purple-50 transition-all duration-200"
          >
            Anuluj
          </button>
        </div>
      </form>
    </div>
  )

  const renderGeneratedRecipe = () => {
    if (!generatedRecipe) return null

    return (
      <div className="p-6 border-b border-teen-purple-200 bg-gradient-to-r from-teen-pink-50 to-teen-purple-50">
        <h3 className="text-lg font-semibold text-teen-purple-700 mb-4 flex items-center">
          <Sparkles className="w-5 h-5 mr-2 text-teen-pink-500" />
          Wygenerowany przepis
        </h3>
        
        <div className="bg-white rounded-lg p-4 border border-teen-purple-200">
          <h4 className="text-xl font-semibold text-teen-purple-700 mb-2">{generatedRecipe.name}</h4>
          {generatedRecipe.description && (
            <p className="text-teen-purple-600 mb-4">{generatedRecipe.description}</p>
          )}
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h5 className="font-medium text-teen-purple-700 mb-2">Składniki:</h5>
              <ul className="space-y-1">
                {generatedRecipe.ingredients.map((ingredient, index) => (
                  <li key={index} className="text-teen-purple-600">
                    • {ingredient.amount} {ingredient.unit} {ingredient.name}
                  </li>
                ))}
              </ul>
            </div>
            
            <div>
              <h5 className="font-medium text-teen-purple-700 mb-2">Instrukcje:</h5>
              <p className="text-teen-purple-600 whitespace-pre-line">{generatedRecipe.instructions}</p>
            </div>
          </div>
          
          <div className="mt-4 flex space-x-3">
            <button
              onClick={() => setGeneratedRecipe(null)}
              className="px-4 py-2 border border-teen-purple-300 text-teen-purple-700 rounded-lg hover:bg-teen-purple-50 transition-all duration-200"
            >
              Zamknij
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-teen-purple-700">Przepisy kulinarne</h2>
          <p className="text-teen-purple-600">Odkryj i twórz pyszne dania</p>
        </div>
        <button
          onClick={() => setShowGenerateForm(true)}
          className="flex items-center px-4 py-2 bg-gradient-to-r from-teen-pink-500 to-teen-purple-500 text-white rounded-lg hover:from-teen-pink-600 hover:to-teen-purple-600 transition-all duration-200"
        >
          <Sparkles className="w-4 h-4 mr-2" />
          Generuj AI
        </button>
      </div>

      {/* Generate Form */}
      {showGenerateForm && renderGenerateForm()}

      {/* Generated Recipe */}
      {generatedRecipe && renderGeneratedRecipe()}

      {/* Search */}
      <div className="mb-6">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-teen-purple-400 w-4 h-4" />
          <input
            type="text"
            placeholder="Wyszukaj przepisy..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-teen-purple-300 rounded-lg focus:ring-2 focus:ring-teen-purple-500 focus:border-transparent"
          />
        </div>
      </div>

      {/* Recipes List */}
      {loading ? (
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-teen-purple-600 mx-auto mb-4"></div>
          <p className="text-teen-purple-600">Ładowanie przepisów...</p>
        </div>
      ) : filteredRecipes.length === 0 ? (
        <div className="text-center py-8">
          <BookOpen className="w-12 h-12 text-teen-purple-400 mx-auto mb-4" />
          <p className="text-teen-purple-600">Brak przepisów do wyświetlenia</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredRecipes.map((recipe) => (
            <div key={recipe.id} className="bg-white border border-teen-purple-200 rounded-lg p-4 hover:shadow-md transition-shadow duration-200">
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <h3 className="font-semibold text-teen-purple-700">{recipe.name}</h3>
                  {recipe.is_ai_generated && (
                    <div className="flex items-center mt-1">
                      <Sparkles className="w-3 h-3 text-teen-pink-500 mr-1" />
                      <span className="text-xs text-teen-pink-600">AI Generated</span>
                    </div>
                  )}
                </div>
                <button
                  onClick={() => handleDeleteRecipe(recipe.id)}
                  className="p-1 text-red-500 hover:text-red-700 hover:bg-red-100 rounded"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
              
              {recipe.description && (
                <p className="text-sm text-teen-purple-600 mb-3 line-clamp-2">{recipe.description}</p>
              )}
              
              <div className="space-y-2">
                <div className="flex items-center text-sm text-teen-purple-600">
                  <Clock className="w-3 h-3 mr-1" />
                  <span>{recipe.cooking_time || 'N/A'} min</span>
                </div>
                
                <div className="flex items-center text-sm text-teen-purple-600">
                  <Users className="w-3 h-3 mr-1" />
                  <span>{recipe.servings || 'N/A'} porcji</span>
                </div>
                
                {recipe.calories_per_serving && (
                  <div className="flex items-center text-sm text-teen-purple-600">
                    <Star className="w-3 h-3 mr-1" />
                    <span>{recipe.calories_per_serving} kcal/porcję</span>
                  </div>
                )}
              </div>
              
              <div className="mt-3 pt-3 border-t border-teen-purple-100">
                <p className="text-xs text-teen-purple-500">
                  {recipe.ingredients.length} składników
                </p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
} 