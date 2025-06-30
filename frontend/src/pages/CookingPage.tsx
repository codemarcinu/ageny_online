import { useState } from 'react'
import { ChefHat, ShoppingCart, BookOpen, Apple, Trophy, Target } from 'lucide-react'
import { useGamification } from '../contexts/GamificationContext'

// Komponenty kulinarne
import ProductsSection from '../components/cooking/ProductsSection'
import RecipesSection from '../components/cooking/RecipesSection'
import ShoppingListSection from '../components/cooking/ShoppingListSection'
import DietPlanSection from '../components/cooking/DietPlanSection'
import CookingChallengesSection from '../components/cooking/CookingChallengesSection'

type CookingSection = 'products' | 'recipes' | 'shopping' | 'diet' | 'challenges'

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
    },
    {
      id: 'diet' as CookingSection,
      name: 'Plan Diety',
      icon: Apple,
      description: 'Planuj posiłki i śledź wartości odżywcze'
    },
    {
      id: 'challenges' as CookingSection,
      name: 'Wyzwania',
      icon: Trophy,
      description: 'Weź udział w wyzwaniach kulinarnych'
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
      case 'diet':
        return <DietPlanSection />
      case 'challenges':
        return <CookingChallengesSection />
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
              Odkryj świat gotowania z pomocą AI - specjalnie dla Ciebie!
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

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl shadow-sm border border-teen-purple-200 p-4">
          <div className="flex items-center space-x-3">
            <div className="bg-teen-pink-100 p-2 rounded-lg">
              <ShoppingCart className="h-5 w-5 text-teen-pink-600" />
            </div>
            <div>
              <div className="text-2xl font-bold text-teen-purple-700">24</div>
              <div className="text-sm text-teen-purple-600">Produkty</div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-teen-purple-200 p-4">
          <div className="flex items-center space-x-3">
            <div className="bg-teen-purple-100 p-2 rounded-lg">
              <BookOpen className="h-5 w-5 text-teen-purple-600" />
            </div>
            <div>
              <div className="text-2xl font-bold text-teen-purple-700">12</div>
              <div className="text-sm text-teen-purple-600">Przepisy</div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-teen-purple-200 p-4">
          <div className="flex items-center space-x-3">
            <div className="bg-green-100 p-2 rounded-lg">
              <Apple className="h-5 w-5 text-green-600" />
            </div>
            <div>
              <div className="text-2xl font-bold text-teen-purple-700">5</div>
              <div className="text-sm text-teen-purple-600">Plany diety</div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-teen-purple-200 p-4">
          <div className="flex items-center space-x-3">
            <div className="bg-yellow-100 p-2 rounded-lg">
              <Trophy className="h-5 w-5 text-yellow-600" />
            </div>
            <div>
              <div className="text-2xl font-bold text-teen-purple-700">8</div>
              <div className="text-sm text-teen-purple-600">Wyzwania</div>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="bg-white rounded-xl shadow-sm border border-teen-purple-200">
        <div className="border-b border-teen-purple-200">
          <nav className="flex space-x-8 px-6 overflow-x-auto">
            {sections.map((section) => {
              const Icon = section.icon
              const isActive = activeSection === section.id
              
              return (
                <button
                  key={section.id}
                  onClick={() => handleSectionChange(section.id)}
                  className={`flex items-center px-3 py-4 text-sm font-medium border-b-2 transition-all duration-200 whitespace-nowrap ${
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

      {/* Motivation Section */}
      <div className="bg-gradient-to-r from-teen-pink-50 to-teen-purple-50 rounded-xl p-6 border border-teen-purple-200">
        <div className="text-center">
          <Target className="h-8 w-8 text-teen-purple-600 mx-auto mb-3" />
          <h3 className="text-lg font-semibold text-teen-purple-700 mb-2">
            Cel na dziś: Przygotuj coś pysznego!
          </h3>
          <p className="text-teen-purple-600 text-sm">
            Każdy posiłek to nowa przygoda kulinarna. Eksperymentuj, baw się i ciesz się gotowaniem! 🍳✨
          </p>
        </div>
      </div>
    </div>
  )
} 