import { motion } from 'framer-motion'
import { Star, TrendingUp, Zap } from 'lucide-react'
import { useGamification } from '../../contexts/GamificationContext'

export default function PointsDisplay() {
  const { state, getLevelProgress } = useGamification()
  const levelProgress = getLevelProgress()

  return (
    <motion.div
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-gradient-to-r from-teen-pink-100 to-teen-purple-100 rounded-xl p-4 border border-teen-pink-200"
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <motion.div
            animate={{ rotate: [0, 10, -10, 0] }}
            transition={{ duration: 0.5, repeat: Infinity, repeatDelay: 2 }}
            className="relative"
          >
            <Star className="w-8 h-8 text-teen-yellow-500 fill-current" />
            <motion.div
              animate={{ scale: [1, 1.2, 1] }}
              transition={{ duration: 1, repeat: Infinity }}
              className="absolute -top-1 -right-1 w-3 h-3 bg-teen-pink-400 rounded-full"
            />
          </motion.div>
          
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-2xl font-bold text-teen-purple-700">
                {state.points}
              </span>
              <span className="text-sm text-teen-purple-600">punktów</span>
            </div>
            <div className="flex items-center space-x-1 text-xs text-teen-purple-500">
              <TrendingUp className="w-3 h-3" />
              <span>Poziom {state.level}</span>
            </div>
          </div>
        </div>

        <div className="text-right">
          <div className="flex items-center space-x-1 text-sm text-teen-purple-600">
            <Zap className="w-4 h-4" />
            <span>Streak: {state.streak} dni</span>
          </div>
          
          {/* Progress bar */}
          <div className="mt-2 w-24 bg-teen-purple-200 rounded-full h-2">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${levelProgress.percentage}%` }}
              transition={{ duration: 0.5 }}
              className="bg-gradient-to-r from-teen-pink-400 to-teen-purple-400 h-2 rounded-full"
            />
          </div>
          <div className="text-xs text-teen-purple-500 mt-1">
            {levelProgress.current}/{levelProgress.next} XP
          </div>
        </div>
      </div>
    </motion.div>
  )
} 