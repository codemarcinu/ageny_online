import { motion } from 'framer-motion'
import { Trophy, Lock, CheckCircle } from 'lucide-react'
import { useGamification } from '../../contexts/GamificationContext'

export default function AchievementsPanel() {
  const { state } = useGamification()
  
  const unlockedCount = state.achievements.filter(a => a.unlocked).length
  const totalCount = state.achievements.length

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      className="bg-white rounded-xl p-6 border border-teen-purple-200 shadow-sm"
    >
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <Trophy className="w-6 h-6 text-teen-yellow-500" />
          <h3 className="text-lg font-semibold text-teen-purple-700">Osiągnięcia</h3>
        </div>
        <div className="text-sm text-teen-purple-600">
          {unlockedCount}/{totalCount}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3">
        {state.achievements.map((achievement, index) => (
          <motion.div
            key={achievement.id}
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: index * 0.1 }}
            className={`relative p-3 rounded-lg border-2 transition-all duration-300 ${
              achievement.unlocked
                ? 'border-teen-mint-300 bg-teen-mint-50'
                : 'border-teen-purple-200 bg-teen-purple-50'
            }`}
          >
            {achievement.unlocked && (
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                className="absolute -top-2 -right-2"
              >
                <CheckCircle className="w-5 h-5 text-teen-mint-500 fill-current" />
              </motion.div>
            )}
            
            <div className="flex items-center space-x-2">
              <div className="text-2xl">{achievement.icon}</div>
              <div className="flex-1 min-w-0">
                <div className={`font-medium text-sm ${
                  achievement.unlocked ? 'text-teen-mint-700' : 'text-teen-purple-700'
                }`}>
                  {achievement.name}
                </div>
                <div className="text-xs text-teen-purple-500 mt-1">
                  {achievement.description}
                </div>
                <div className="flex items-center justify-between mt-2">
                  <span className="text-xs text-teen-purple-600">
                    +{achievement.points} pkt
                  </span>
                  {achievement.unlocked && (
                    <span className="text-xs text-teen-mint-600">
                      {achievement.unlockedAt && 
                        new Date(achievement.unlockedAt).toLocaleDateString('pl-PL')
                      }
                    </span>
                  )}
                </div>
              </div>
            </div>

            {!achievement.unlocked && (
              <motion.div
                animate={{ opacity: [0.3, 0.7, 0.3] }}
                transition={{ duration: 2, repeat: Infinity }}
                className="absolute inset-0 bg-teen-purple-100 rounded-lg flex items-center justify-center"
              >
                <Lock className="w-4 h-4 text-teen-purple-400" />
              </motion.div>
            )}
          </motion.div>
        ))}
      </div>

      {/* Progress indicator */}
      <div className="mt-4">
        <div className="flex justify-between text-sm text-teen-purple-600 mb-1">
          <span>Postęp</span>
          <span>{Math.round((unlockedCount / totalCount) * 100)}%</span>
        </div>
        <div className="w-full bg-teen-purple-200 rounded-full h-2">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${(unlockedCount / totalCount) * 100}%` }}
            transition={{ duration: 0.5 }}
            className="bg-gradient-to-r from-teen-mint-400 to-teen-purple-400 h-2 rounded-full"
          />
        </div>
      </div>
    </motion.div>
  )
} 