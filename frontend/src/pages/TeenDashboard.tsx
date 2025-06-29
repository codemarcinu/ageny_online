import { motion } from 'framer-motion'
import { Sparkles, Heart, MessageCircle, Camera, Star, Trophy, Target } from 'lucide-react'
import { useGamification } from '../contexts/GamificationContext'
import PointsDisplay from '../components/gamification/PointsDisplay'
import AchievementsPanel from '../components/gamification/AchievementsPanel'
import DailyChallenges from '../components/gamification/DailyChallenges'

export default function TeenDashboard() {
  const { state } = useGamification()

  const quickActions = [
    {
      name: 'Rozmowa z AI',
      description: 'Zadaj pytanie swojemu asystentowi',
      icon: MessageCircle,
      color: 'from-teen-pink-400 to-teen-pink-600',
      bgColor: 'bg-teen-pink-50',
      borderColor: 'border-teen-pink-200',
      href: '/chat'
    },
    {
      name: 'Skanowanie dokumentów',
      description: 'Przeskanuj i przeczytaj tekst',
      icon: Camera,
      color: 'from-teen-mint-400 to-teen-mint-600',
      bgColor: 'bg-teen-mint-50',
      borderColor: 'border-teen-mint-200',
      href: '/ocr'
    },
    {
      name: 'Wyszukiwanie w sieci',
      description: 'Znajdź aktualne informacje',
      icon: Sparkles,
      color: 'from-teen-purple-400 to-teen-purple-600',
      bgColor: 'bg-teen-purple-50',
      borderColor: 'border-teen-purple-200',
      href: '/web-search'
    }
  ]

  const stats = [
    {
      label: 'Poziom',
      value: state.level,
      icon: Star,
      color: 'text-teen-yellow-500'
    },
    {
      label: 'Punkty',
      value: state.points,
      icon: Trophy,
      color: 'text-teen-pink-500'
    },
    {
      label: 'Streak',
      value: `${state.streak} dni`,
      icon: Heart,
      color: 'text-teen-purple-500'
    }
  ]

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Welcome Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center mb-8"
      >
        <motion.div
          animate={{ rotate: [0, 5, -5, 0] }}
          transition={{ duration: 2, repeat: Infinity, repeatDelay: 3 }}
          className="inline-block mb-4"
        >
          <Sparkles className="w-12 h-12 text-teen-purple-500 mx-auto" />
        </motion.div>
        <h1 className="text-3xl font-bold bg-gradient-to-r from-teen-pink-600 to-teen-purple-600 bg-clip-text text-transparent mb-2">
          Witaj w Ageny! ✨
        </h1>
        <p className="text-teen-purple-600 text-lg">
          Twój osobisty asystent AI gotowy do pomocy!
        </p>
      </motion.div>

      {/* Stats Cards */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8"
      >
        {stats.map((stat, index) => {
          const Icon = stat.icon
          return (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.3 + index * 0.1 }}
              className="bg-white rounded-xl p-6 border border-teen-purple-200 shadow-sm hover:shadow-md transition-shadow"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-teen-purple-600">{stat.label}</p>
                  <p className="text-2xl font-bold text-teen-purple-700">{stat.value}</p>
                </div>
                <Icon className={`w-8 h-8 ${stat.color}`} />
              </div>
            </motion.div>
          )
        })}
      </motion.div>

      {/* Points Display */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="mb-8"
      >
        <PointsDisplay />
      </motion.div>

      {/* Quick Actions */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="mb-8"
      >
        <h2 className="text-xl font-semibold text-teen-purple-700 mb-4 flex items-center">
          <Target className="w-5 h-5 mr-2 text-teen-pink-500" />
          Szybkie akcje
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {quickActions.map((action, index) => {
            const Icon = action.icon
            return (
              <motion.a
                key={action.name}
                href={action.href}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.6 + index * 0.1 }}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className={`${action.bgColor} ${action.borderColor} border-2 rounded-xl p-6 hover:shadow-lg transition-all duration-300 group`}
              >
                <div className="flex items-center space-x-4">
                  <div className={`p-3 rounded-lg bg-gradient-to-r ${action.color} group-hover:scale-110 transition-transform`}>
                    <Icon className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-teen-purple-700 group-hover:text-teen-purple-800 transition-colors">
                      {action.name}
                    </h3>
                    <p className="text-sm text-teen-purple-600 mt-1">
                      {action.description}
                    </p>
                  </div>
                </div>
              </motion.a>
            )
          })}
        </div>
      </motion.div>

      {/* Gamification Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.7 }}
        className="grid grid-cols-1 lg:grid-cols-2 gap-8"
      >
        <DailyChallenges />
        <AchievementsPanel />
      </motion.div>

      {/* Fun Facts Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.8 }}
        className="mt-8 bg-gradient-to-r from-teen-pink-50 to-teen-purple-50 rounded-xl p-6 border border-teen-pink-200"
      >
        <h3 className="text-lg font-semibold text-teen-purple-700 mb-4 flex items-center">
          <Sparkles className="w-5 h-5 mr-2 text-teen-pink-500" />
          Ciekawostki o AI
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-teen-purple-600">
          <div className="flex items-start space-x-2">
            <span className="text-teen-pink-500">💡</span>
            <span>AI może pomóc w odrabianiu zadań domowych i nauce!</span>
          </div>
          <div className="flex items-start space-x-2">
            <span className="text-teen-mint-500">🎨</span>
            <span>Możesz poprosić AI o pomoc w projektach kreatywnych</span>
          </div>
          <div className="flex items-start space-x-2">
            <span className="text-teen-purple-500">📚</span>
            <span>AI zna odpowiedzi na prawie każde pytanie</span>
          </div>
          <div className="flex items-start space-x-2">
            <span className="text-teen-yellow-500">🌟</span>
            <span>Im więcej rozmawiasz, tym więcej punktów zdobywasz!</span>
          </div>
        </div>
      </motion.div>
    </div>
  )
} 