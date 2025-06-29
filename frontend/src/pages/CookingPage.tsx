import { useState } from 'react'
import { ChefHat, ShoppingCart, BookOpen } from 'lucide-react'
import { useGamification } from '../contexts/GamificationContext'

// Komponenty kulinarne
import ProductsSection from '../components/cooking/ProductsSection'
import RecipesSection from '../components/cooking/RecipesSection'
import ShoppingListSection from '../components/cooking/ShoppingListSection'

type CookingSection = 'products' | 'recipes' | 'shopping'

export default function CookingPage() {
  const [activeSection, setActiveSection] = useState<CookingSection>('products')
  const { addPoints } = useGamification()

  const sections = [
    {
      id: 'products' as CookingSection,
      name: 'Produkty',
      icon: ShoppingCart,
      description: 'Zarządzaj produktami spożywczymi'
    },
    {
      id: 'recipes' as CookingSection,
      name: 'Przepisy',
      icon: BookOpen,
      description: 'Przeglądaj i twórz przepisy'
    },
    {
      id: 'shopping' as CookingSection,
      name: 'Listy zakupów',
      icon: ChefHat,
      description: 'Planuj zakupy i oszczędzaj'
    }
  ]

  const handleSectionChange = (section: CookingSection) => {
    setActiveSection(section)
    // Dodaj punkty za nawigację
    addPoints(1)
  }

  const renderActiveSection = () => {
    switch (activeSection) {
      case 'products':
        return <ProductsSection />
      case 'recipes':
        return <RecipesSection />
      case 'shopping':
        return <ShoppingListSection />
      default:
        return <ProductsSection />
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-xl shadow-sm border border-teen-purple-200 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-teen-pink-600 to-teen-purple-600 bg-clip-text text-transparent">
              🍳 Kuchnia Antoniny
            </h1>
            <p className="text-teen-purple-600 mt-2">
              Odkryj świat gotowania z pomocą AI
            </p>
          </div>
          <div className="flex items-center space-x-3">
            <div className="bg-gradient-to-r from-teen-pink-100 to-teen-purple-100 px-4 py-2 rounded-full">
              <span className="text-teen-purple-700 font-medium">
                🎯 Gotuj z pasją!
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="bg-white rounded-xl shadow-sm border border-teen-purple-200">
        <div className="border-b border-teen-purple-200">
          <nav className="flex space-x-8 px-6">
            {sections.map((section) => {
              const Icon = section.icon
              const isActive = activeSection === section.id
              
              return (
                <button
                  key={section.id}
                  onClick={() => handleSectionChange(section.id)}
                  className={`flex items-center px-3 py-4 text-sm font-medium border-b-2 transition-all duration-200 ${
                    isActive
                      ? 'border-teen-purple-500 text-teen-purple-600 bg-teen-purple-50'
                      : 'border-transparent text-teen-purple-500 hover:text-teen-purple-700 hover:border-teen-purple-300 hover:bg-teen-purple-25'
                  }`}
                >
                  <Icon className="w-4 h-4 mr-2" />
                  {section.name}
                </button>
              )
            })}
          </nav>
        </div>
        
        {/* Section Description */}
        <div className="px-6 py-4 bg-teen-purple-25">
          <p className="text-teen-purple-600 text-sm">
            {sections.find(s => s.id === activeSection)?.description}
          </p>
        </div>
      </div>

      {/* Active Section Content */}
      <div className="bg-white rounded-xl shadow-sm border border-teen-purple-200">
        {renderActiveSection()}
      </div>
    </div>
  )
} 