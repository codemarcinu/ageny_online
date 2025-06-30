import { useState, useEffect, useRef } from 'react'
import { Plus, Search, Edit, Trash2, Tag, DollarSign, Camera } from 'lucide-react'
import { useApi } from '../../contexts/ApiContext'
import { useGamification } from '../../contexts/GamificationContext'
import toast from 'react-hot-toast'

interface Product {
  id: number
  name: string
  category: string
  price_per_unit: number
  unit: string
  nutritional_value?: {
    calories?: number
    protein?: number
    carbs?: number
    fat?: number
  }
  created_at: string
  updated_at: string
}

interface AddProductForm {
  name: string
  category: string
  price_per_unit: number
  unit: string
  calories?: number
  protein?: number
  carbs?: number
  fat?: number
}

const USER_ID = 1;

export default function ProductsSection() {
  const [products, setProducts] = useState<Product[]>([])
  const [categories, setCategories] = useState<string[]>([])
  const [loading, setLoading] = useState(true)
  const [showAddForm, setShowAddForm] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('')
  const [editingProduct, setEditingProduct] = useState<Product | null>(null)
  const [scanning, setScanning] = useState(false)
  
  const { api } = useApi()
  const { addPoints, unlockAchievement, checkCookingEnthusiast } = useGamification()
  const fileInputRef = useRef<HTMLInputElement>(null)

  const [formData, setFormData] = useState<AddProductForm>({
    name: '',
    category: '',
    price_per_unit: 0,
    unit: 'kg',
    calories: 0,
    protein: 0,
    carbs: 0,
    fat: 0
  })

  // Pobierz produkty i kategorie
  useEffect(() => {
    fetchProducts()
    fetchCategories()
  }, [])

  const fetchProducts = async () => {
    try {
      setLoading(true)
      const response = await api.get('/v2/cooking/products/list', { params: { user_id: USER_ID } })
      setProducts(response.data.products || [])
    } catch (error) {
      console.error('Błąd podczas pobierania produktów:', error)
      toast.error('Nie udało się pobrać produktów')
    } finally {
      setLoading(false)
    }
  }

  const fetchCategories = async () => {
    try {
      const response = await api.get('/v2/cooking/products/categories', { params: { user_id: USER_ID } })
      setCategories(response.data.categories || [])
    } catch (error) {
      console.error('Błąd podczas pobierania kategorii:', error)
    }
  }

  const handleAddProduct = async (e: React.FormEvent) => {
    e.preventDefault()
    
    try {
      await api.post('/v2/cooking/products/add', {
        ...formData,
        user_id: USER_ID
      })
      
      toast.success('Produkt został dodany!')
      addPoints(5)
      
      // Sprawdź osiągnięcia
      const newProductCount = products.length + 1
      if (newProductCount === 1) {
        unlockAchievement('first-product')
        checkCookingEnthusiast()
      }
      if (newProductCount === 10) {
        unlockAchievement('product-collector')
      }
      
      // Sprawdź czy produkt ma pełne wartości odżywcze
      if (formData.calories && formData.protein && formData.carbs && formData.fat) {
        const nutritionProducts = products.filter(p => 
          p.nutritional_value?.calories && 
          p.nutritional_value?.protein && 
          p.nutritional_value?.carbs && 
          p.nutritional_value?.fat
        ).length + 1
        
        if (nutritionProducts === 5) {
          unlockAchievement('nutrition-expert')
        }
      }
      
      setShowAddForm(false)
      resetForm()
      fetchProducts()
    } catch (error) {
      console.error('Błąd podczas dodawania produktu:', error)
      toast.error('Nie udało się dodać produktu')
    }
  }

  const handleEditProduct = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!editingProduct) return
    
    try {
      await api.put(`/v2/cooking/products/${editingProduct.id}`, {
        ...formData,
        user_id: USER_ID
      })
      
      toast.success('Produkt został zaktualizowany!')
      addPoints(3)
      setEditingProduct(null)
      resetForm()
      fetchProducts()
    } catch (error) {
      console.error('Błąd podczas edycji produktu:', error)
      toast.error('Nie udało się zaktualizować produktu')
    }
  }

  const handleDeleteProduct = async (productId: number) => {
    if (!confirm('Czy na pewno chcesz usunąć ten produkt?')) return
    
    try {
      await api.delete(`/v2/cooking/products/${productId}`)
      toast.success('Produkt został usunięty')
      addPoints(2)
      fetchProducts()
    } catch (error) {
      console.error('Błąd podczas usuwania produktu:', error)
      toast.error('Nie udało się usunąć produktu')
    }
  }

  const resetForm = () => {
    setFormData({
      name: '',
      category: '',
      price_per_unit: 0,
      unit: 'kg',
      calories: 0,
      protein: 0,
      carbs: 0,
      fat: 0
    })
  }

  const startEdit = (product: Product) => {
    setEditingProduct(product)
    setFormData({
      name: product.name,
      category: product.category,
      price_per_unit: product.price_per_unit,
      unit: product.unit,
      calories: product.nutritional_value?.calories || 0,
      protein: product.nutritional_value?.protein || 0,
      carbs: product.nutritional_value?.carbs || 0,
      fat: product.nutritional_value?.fat || 0
    })
  }

  const filteredProducts = products.filter(product => {
    const matchesSearch = product.name.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesCategory = !selectedCategory || product.category === selectedCategory
    return matchesSearch && matchesCategory
  })

  const handleScanProduct = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    // Validate file type
    if (!file.type.startsWith('image/')) {
      toast.error('Proszę wybrać plik obrazu')
      return
    }

    // Validate file size (10MB limit)
    if (file.size > 10 * 1024 * 1024) {
      toast.error('Plik jest za duży (maksymalnie 10MB)')
      return
    }

    try {
      setScanning(true)
      
      const formData = new FormData()
      formData.append('image', file)
      
      const response = await api.post('/v2/cooking/products/scan', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        params: {
          user_id: USER_ID
        }
      })
      
      if (response.data && response.data.length > 0) {
        toast.success('Produkt został zeskanowany i dodany!')
        addPoints(8) // Bonus points for scanning
        unlockAchievement('product-scanner')
        checkCookingEnthusiast()
        fetchProducts()
      } else {
        toast.error('Nie udało się rozpoznać produktu')
      }
    } catch (error) {
      console.error('Błąd podczas skanowania produktu:', error)
      toast.error('Błąd podczas skanowania produktu')
    } finally {
      setScanning(false)
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
    }
  }

  const triggerFileInput = () => {
    fileInputRef.current?.click()
  }

  const renderProductForm = () => (
    <div className="p-6 border-b border-teen-purple-200">
      <h3 className="text-lg font-semibold text-teen-purple-700 mb-4">
        {editingProduct ? 'Edytuj produkt' : 'Dodaj nowy produkt'}
      </h3>
      
      <form onSubmit={editingProduct ? handleEditProduct : handleAddProduct} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-teen-purple-700 mb-1">
              Nazwa produktu
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({...formData, name: e.target.value})}
              className="w-full px-3 py-2 border border-teen-purple-300 rounded-lg focus:ring-2 focus:ring-teen-purple-500 focus:border-transparent"
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-teen-purple-700 mb-1">
              Kategoria
            </label>
            <select
              value={formData.category}
              onChange={(e) => setFormData({...formData, category: e.target.value})}
              className="w-full px-3 py-2 border border-teen-purple-300 rounded-lg focus:ring-2 focus:ring-teen-purple-500 focus:border-transparent"
              required
            >
              <option value="">Wybierz kategorię</option>
              {categories.map(category => (
                <option key={category} value={category}>{category}</option>
              ))}
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-teen-purple-700 mb-1">
              Cena za jednostkę
            </label>
            <input
              type="number"
              step="0.01"
              value={formData.price_per_unit}
              onChange={(e) => setFormData({...formData, price_per_unit: parseFloat(e.target.value)})}
              className="w-full px-3 py-2 border border-teen-purple-300 rounded-lg focus:ring-2 focus:ring-teen-purple-500 focus:border-transparent"
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-teen-purple-700 mb-1">
              Jednostka
            </label>
            <select
              value={formData.unit}
              onChange={(e) => setFormData({...formData, unit: e.target.value})}
              className="w-full px-3 py-2 border border-teen-purple-300 rounded-lg focus:ring-2 focus:ring-teen-purple-500 focus:border-transparent"
            >
              <option value="kg">kg</option>
              <option value="g">g</option>
              <option value="l">l</option>
              <option value="ml">ml</option>
              <option value="szt">szt</option>
            </select>
          </div>
        </div>
        
        <div className="border-t border-teen-purple-200 pt-4">
          <h4 className="text-sm font-medium text-teen-purple-700 mb-3">Wartości odżywcze (na 100g)</h4>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm text-teen-purple-600 mb-1">Kalorie</label>
              <input
                type="number"
                value={formData.calories}
                onChange={(e) => setFormData({...formData, calories: parseInt(e.target.value)})}
                className="w-full px-3 py-2 border border-teen-purple-300 rounded-lg focus:ring-2 focus:ring-teen-purple-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm text-teen-purple-600 mb-1">Białko (g)</label>
              <input
                type="number"
                step="0.1"
                value={formData.protein}
                onChange={(e) => setFormData({...formData, protein: parseFloat(e.target.value)})}
                className="w-full px-3 py-2 border border-teen-purple-300 rounded-lg focus:ring-2 focus:ring-teen-purple-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm text-teen-purple-600 mb-1">Węglowodany (g)</label>
              <input
                type="number"
                step="0.1"
                value={formData.carbs}
                onChange={(e) => setFormData({...formData, carbs: parseFloat(e.target.value)})}
                className="w-full px-3 py-2 border border-teen-purple-300 rounded-lg focus:ring-2 focus:ring-teen-purple-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm text-teen-purple-600 mb-1">Tłuszcze (g)</label>
              <input
                type="number"
                step="0.1"
                value={formData.fat}
                onChange={(e) => setFormData({...formData, fat: parseFloat(e.target.value)})}
                className="w-full px-3 py-2 border border-teen-purple-300 rounded-lg focus:ring-2 focus:ring-teen-purple-500 focus:border-transparent"
              />
            </div>
          </div>
        </div>
        
        <div className="flex space-x-3">
          <button
            type="submit"
            className="px-4 py-2 bg-gradient-to-r from-teen-pink-500 to-teen-purple-500 text-white rounded-lg hover:from-teen-pink-600 hover:to-teen-purple-600 transition-all duration-200"
          >
            {editingProduct ? 'Zaktualizuj' : 'Dodaj produkt'}
          </button>
          <button
            type="button"
            onClick={() => {
              setShowAddForm(false)
              setEditingProduct(null)
              resetForm()
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
    <div className="bg-white rounded-xl shadow-lg overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-teen-purple-500 to-teen-pink-500 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-white">Produkty Spożywcze</h2>
            <p className="text-teen-purple-100 mt-1">
              Zarządzaj swoimi produktami i wartościami odżywczymi
            </p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={triggerFileInput}
              disabled={scanning}
              className="flex items-center gap-2 px-4 py-2 bg-white/20 hover:bg-white/30 text-white rounded-lg transition-colors disabled:opacity-50"
            >
              <Camera size={20} />
              {scanning ? 'Skanowanie...' : 'Skanuj produkt'}
            </button>
            <button
              onClick={() => setShowAddForm(!showAddForm)}
              className="flex items-center gap-2 px-4 py-2 bg-white/20 hover:bg-white/30 text-white rounded-lg transition-colors"
            >
              <Plus size={20} />
              Dodaj produkt
            </button>
          </div>
        </div>
      </div>

      {/* Hidden file input for scanning */}
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        onChange={handleScanProduct}
        className="hidden"
      />

      {/* Add/Edit Form */}
      {(showAddForm || editingProduct) && renderProductForm()}

      {/* Filters */}
      <div className="flex flex-col md:flex-row gap-4 mb-6">
        <div className="flex-1">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-teen-purple-400 w-4 h-4" />
            <input
              type="text"
              placeholder="Wyszukaj produkty..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-teen-purple-300 rounded-lg focus:ring-2 focus:ring-teen-purple-500 focus:border-transparent"
            />
          </div>
        </div>
        <div className="md:w-48">
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="w-full px-3 py-2 border border-teen-purple-300 rounded-lg focus:ring-2 focus:ring-teen-purple-500 focus:border-transparent"
          >
            <option value="">Wszystkie kategorie</option>
            {categories.map(category => (
              <option key={category} value={category}>{category}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Products List */}
      {loading ? (
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-teen-purple-600 mx-auto mb-4"></div>
          <p className="text-teen-purple-600">Ładowanie produktów...</p>
        </div>
      ) : filteredProducts.length === 0 ? (
        <div className="text-center py-8">
          <Tag className="w-12 h-12 text-teen-purple-400 mx-auto mb-4" />
          <p className="text-teen-purple-600">Brak produktów do wyświetlenia</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredProducts.map((product) => (
            <div key={product.id} className="bg-white border border-teen-purple-200 rounded-lg p-4 hover:shadow-md transition-shadow duration-200">
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <h3 className="font-semibold text-teen-purple-700">{product.name}</h3>
                  <div className="flex items-center mt-1">
                    <Tag className="w-3 h-3 text-teen-purple-400 mr-1" />
                    <span className="text-sm text-teen-purple-600">{product.category}</span>
                  </div>
                </div>
                <div className="flex space-x-2">
                  <button
                    onClick={() => startEdit(product)}
                    className="p-1 text-teen-purple-500 hover:text-teen-purple-700 hover:bg-teen-purple-100 rounded"
                  >
                    <Edit className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => handleDeleteProduct(product.id)}
                    className="p-1 text-red-500 hover:text-red-700 hover:bg-red-100 rounded"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
              
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-teen-purple-600">Cena:</span>
                  <div className="flex items-center">
                    <DollarSign className="w-3 h-3 text-teen-purple-400 mr-1" />
                    <span className="font-medium text-teen-purple-700">
                      {product.price_per_unit.toFixed(2)} zł/{product.unit}
                    </span>
                  </div>
                </div>
                
                {product.nutritional_value && (
                  <div className="pt-2 border-t border-teen-purple-100">
                    <div className="grid grid-cols-2 gap-2 text-xs">
                      {product.nutritional_value.calories && (
                        <div className="flex justify-between">
                          <span className="text-teen-purple-600">Kalorie:</span>
                          <span className="font-medium">{product.nutritional_value.calories} kcal</span>
                        </div>
                      )}
                      {product.nutritional_value.protein && (
                        <div className="flex justify-between">
                          <span className="text-teen-purple-600">Białko:</span>
                          <span className="font-medium">{product.nutritional_value.protein}g</span>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
} 