import { useState, useEffect } from 'react'
import { Plus, ShoppingCart, DollarSign, CheckCircle, Trash2, Sparkles } from 'lucide-react'
import { useApi } from '../../contexts/ApiContext'
import { useGamification } from '../../contexts/GamificationContext'
import toast from 'react-hot-toast'

interface ShoppingList {
  id: number
  name: string
  items: Array<{
    product_name: string
    quantity: number
    unit: string
    estimated_cost: number
  }>
  total_estimated_cost: number
  is_completed: boolean
  created_at: string
  updated_at: string
}

interface CreateListForm {
  name: string
  items: Array<{
    product_name: string
    quantity: number
    unit: string
  }>
  budget?: number
}

export default function ShoppingListSection() {
  const [shoppingLists, setShoppingLists] = useState<ShoppingList[]>([])
  const [loading, setLoading] = useState(true)
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [optimizing, setOptimizing] = useState(false)
  
  const { api } = useApi()
  const { addPoints, unlockAchievement, checkCookingEnthusiast } = useGamification()

  const [createForm, setCreateForm] = useState<CreateListForm>({
    name: '',
    items: [{ product_name: '', quantity: 1, unit: 'kg' }],
    budget: 100
  })

  useEffect(() => {
    fetchShoppingLists()
  }, [])

  const fetchShoppingLists = async () => {
    try {
      setLoading(true)
      const response = await api.get('/v2/cooking/shopping/list')
      setShoppingLists(response.data.shopping_lists || [])
    } catch (error) {
      console.error('Błąd podczas pobierania list zakupów:', error)
      toast.error('Nie udało się pobrać list zakupów')
    } finally {
      setLoading(false)
    }
  }

  const handleCreateList = async (e: React.FormEvent) => {
    e.preventDefault()
    
    try {
      await api.post('/v2/cooking/shopping/create', {
        ...createForm,
        user_id: 1
      })
      
      toast.success('Lista zakupów została utworzona!')
      addPoints(5)
      
      // Sprawdź osiągnięcia
      const newListCount = shoppingLists.length + 1
      if (newListCount === 1) {
        unlockAchievement('shopping-list-creator')
        checkCookingEnthusiast()
      }
      
      setShowCreateForm(false)
      resetCreateForm()
      fetchShoppingLists()
    } catch (error) {
      console.error('Błąd podczas tworzenia listy zakupów:', error)
      toast.error('Nie udało się utworzyć listy zakupów')
    }
  }

  const handleOptimizeList = async (listId: number) => {
    try {
      setOptimizing(true)
      await api.post(`/v2/cooking/shopping/optimize`, {
        shopping_list_id: listId,
        budget: createForm.budget || 100
      }, {
        params: { user_id: 1 }
      })
      
      toast.success('Lista została zoptymalizowana!')
      addPoints(8)
      fetchShoppingLists()
    } catch (error) {
      console.error('Błąd podczas optymalizacji listy:', error)
      toast.error('Nie udało się zoptymalizować listy')
    } finally {
      setOptimizing(false)
    }
  }

  const handleCompleteList = async (listId: number) => {
    try {
      await api.put(`/v2/cooking/shopping/${listId}/complete`)
      toast.success('Lista została oznaczona jako zakończona!')
      addPoints(3)
      fetchShoppingLists()
    } catch (error) {
      console.error('Błąd podczas oznaczania listy jako zakończonej:', error)
      toast.error('Nie udało się zakończyć listy')
    }
  }

  const handleDeleteList = async (listId: number) => {
    if (!confirm('Czy na pewno chcesz usunąć tę listę zakupów?')) return
    
    try {
      await api.delete(`/v2/cooking/shopping/${listId}`)
      toast.success('Lista została usunięta')
      addPoints(2)
      fetchShoppingLists()
    } catch (error) {
      console.error('Błąd podczas usuwania listy:', error)
      toast.error('Nie udało się usunąć listy')
    }
  }

  const resetCreateForm = () => {
    setCreateForm({
      name: '',
      items: [{ product_name: '', quantity: 1, unit: 'kg' }],
      budget: 100
    })
  }

  const addItem = () => {
    setCreateForm({
      ...createForm,
      items: [...createForm.items, { product_name: '', quantity: 1, unit: 'kg' }]
    })
  }

  const removeItem = (index: number) => {
    setCreateForm({
      ...createForm,
      items: createForm.items.filter((_, i) => i !== index)
    })
  }

  const renderCreateForm = () => (
    <div className="p-6 border-b border-teen-purple-200">
      <h3 className="text-lg font-semibold text-teen-purple-700 mb-4">Utwórz nową listę zakupów</h3>
      
      <form onSubmit={handleCreateList} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-teen-purple-700 mb-1">
            Nazwa listy
          </label>
          <input
            type="text"
            value={createForm.name}
            onChange={(e) => setCreateForm({...createForm, name: e.target.value})}
            placeholder="np. Zakupy na weekend"
            className="w-full px-3 py-2 border border-teen-purple-300 rounded-lg focus:ring-2 focus:ring-teen-purple-500 focus:border-transparent"
            required
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-teen-purple-700 mb-1">
            Budżet (zł)
          </label>
          <input
            type="number"
            value={createForm.budget}
            onChange={(e) => setCreateForm({...createForm, budget: parseInt(e.target.value)})}
            className="w-full px-3 py-2 border border-teen-purple-300 rounded-lg focus:ring-2 focus:ring-teen-purple-500 focus:border-transparent"
            min="0"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-teen-purple-700 mb-2">
            Produkty
          </label>
          {createForm.items.map((item, index) => (
            <div key={index} className="flex gap-2 mb-2">
              <input
                type="text"
                value={item.product_name}
                onChange={(e) => {
                  const newItems = [...createForm.items]
                  newItems[index].product_name = e.target.value
                  setCreateForm({ ...createForm, items: newItems })
                }}
                placeholder="Nazwa produktu"
                className="flex-1 px-3 py-2 border border-teen-purple-300 rounded-lg focus:ring-2 focus:ring-teen-purple-500 focus:border-transparent"
                required
              />
              <input
                type="number"
                value={item.quantity}
                onChange={(e) => {
                  const newItems = [...createForm.items]
                  newItems[index].quantity = parseFloat(e.target.value)
                  setCreateForm({ ...createForm, items: newItems })
                }}
                className="w-20 px-3 py-2 border border-teen-purple-300 rounded-lg focus:ring-2 focus:ring-teen-purple-500 focus:border-transparent"
                min="0"
                step="0.1"
                required
              />
              <select
                value={item.unit}
                onChange={(e) => {
                  const newItems = [...createForm.items]
                  newItems[index].unit = e.target.value
                  setCreateForm({ ...createForm, items: newItems })
                }}
                className="w-20 px-3 py-2 border border-teen-purple-300 rounded-lg focus:ring-2 focus:ring-teen-purple-500 focus:border-transparent"
              >
                <option value="kg">kg</option>
                <option value="g">g</option>
                <option value="l">l</option>
                <option value="ml">ml</option>
                <option value="szt">szt</option>
              </select>
              {createForm.items.length > 1 && (
                <button
                  type="button"
                  onClick={() => removeItem(index)}
                  className="px-3 py-2 text-red-500 hover:text-red-700 hover:bg-red-100 rounded-lg"
                >
                  Usuń
                </button>
              )}
            </div>
          ))}
          <button
            type="button"
            onClick={addItem}
            className="text-teen-purple-600 hover:text-teen-purple-700 text-sm"
          >
            + Dodaj produkt
          </button>
        </div>
        
        <div className="flex space-x-3">
          <button
            type="submit"
            className="px-4 py-2 bg-gradient-to-r from-teen-pink-500 to-teen-purple-500 text-white rounded-lg hover:from-teen-pink-600 hover:to-teen-purple-600 transition-all duration-200"
          >
            Utwórz listę
          </button>
          <button
            type="button"
            onClick={() => {
              setShowCreateForm(false)
              resetCreateForm()
            }}
            className="px-4 py-2 border border-teen-purple-300 text-teen-purple-700 rounded-lg hover:bg-teen-purple-50 transition-all duration-200"
          >
            Anuluj
          </button>
        </div>
      </form>
    </div>
  )

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-teen-purple-700">Listy zakupów</h2>
          <p className="text-teen-purple-600">Planuj zakupy i oszczędzaj pieniądze</p>
        </div>
        <button
          onClick={() => setShowCreateForm(true)}
          className="flex items-center px-4 py-2 bg-gradient-to-r from-teen-pink-500 to-teen-purple-500 text-white rounded-lg hover:from-teen-pink-600 hover:to-teen-purple-600 transition-all duration-200"
        >
          <Plus className="w-4 h-4 mr-2" />
          Nowa lista
        </button>
      </div>

      {/* Create Form */}
      {showCreateForm && renderCreateForm()}

      {/* Shopping Lists */}
      {loading ? (
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-teen-purple-600 mx-auto mb-4"></div>
          <p className="text-teen-purple-600">Ładowanie list zakupów...</p>
        </div>
      ) : shoppingLists.length === 0 ? (
        <div className="text-center py-8">
          <ShoppingCart className="w-12 h-12 text-teen-purple-400 mx-auto mb-4" />
          <p className="text-teen-purple-600">Brak list zakupów do wyświetlenia</p>
        </div>
      ) : (
        <div className="space-y-4">
          {shoppingLists.map((list) => (
            <div key={list.id} className={`bg-white border rounded-lg p-4 hover:shadow-md transition-shadow duration-200 ${
              list.is_completed 
                ? 'border-teen-mint-300 bg-teen-mint-50' 
                : 'border-teen-purple-200'
            }`}>
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <h3 className="font-semibold text-teen-purple-700">{list.name}</h3>
                    {list.is_completed && (
                      <CheckCircle className="w-5 h-5 text-teen-mint-500" />
                    )}
                  </div>
                  <p className="text-sm text-teen-purple-600 mt-1">
                    {list.items.length} produktów • 
                    <span className="font-medium text-teen-purple-700 ml-1">
                      {list.total_estimated_cost.toFixed(2)} zł
                    </span>
                  </p>
                </div>
                
                <div className="flex space-x-2">
                  {!list.is_completed && (
                    <>
                      <button
                        onClick={() => handleOptimizeList(list.id)}
                        disabled={optimizing}
                        className="flex items-center px-3 py-1 text-teen-purple-600 hover:text-teen-purple-700 hover:bg-teen-purple-100 rounded text-sm"
                      >
                        <Sparkles className="w-3 h-3 mr-1" />
                        Optymalizuj
                      </button>
                      <button
                        onClick={() => handleCompleteList(list.id)}
                        className="flex items-center px-3 py-1 text-teen-mint-600 hover:text-teen-mint-700 hover:bg-teen-mint-100 rounded text-sm"
                      >
                        <CheckCircle className="w-3 h-3 mr-1" />
                        Zakończ
                      </button>
                    </>
                  )}
                  <button
                    onClick={() => handleDeleteList(list.id)}
                    className="p-1 text-red-500 hover:text-red-700 hover:bg-red-100 rounded"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
              
              <div className="space-y-2">
                {list.items.map((item, index) => (
                  <div key={index} className="flex items-center justify-between text-sm">
                    <span className="text-teen-purple-700">
                      {item.quantity} {item.unit} {item.product_name}
                    </span>
                    <span className="text-teen-purple-600 font-medium">
                      {item.estimated_cost.toFixed(2)} zł
                    </span>
                  </div>
                ))}
              </div>
              
              <div className="mt-4 pt-3 border-t border-teen-purple-100">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-teen-purple-600">Szacowany koszt całkowity:</span>
                  <div className="flex items-center">
                    <DollarSign className="w-4 h-4 text-teen-purple-400 mr-1" />
                    <span className="font-semibold text-teen-purple-700">
                      {list.total_estimated_cost.toFixed(2)} zł
                    </span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
} 