import { motion } from 'framer-motion'
import { Target, Calendar, CheckCircle, Clock } from 'lucide-react'
import { useGamification } from '../../contexts/GamificationContext'

export default function DailyChallenges() {
  const { state } = useGamification()
  
  const activeChallenges = state.challenges.filter(c => !c.completed)
  const completedChallenges = state.challenges.filter(c => c.completed)

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      className="bg-white rounded-xl p-6 border border-teen-purple-200 shadow-sm"
    >
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <Target className="w-6 h-6 text-teen-pink-500" />
          <h3 className="text-lg font-semibold text-teen-purple-700">Dzisiejsze wyzwania</h3>
        </div>
        <div className="flex items-center space-x-1 text-sm text-teen-purple-600">
          <Calendar className="w-4 h-4" />
          <span>{new Date().toLocaleDateString('pl-PL')}</span>
        </div>
      </div>

      {activeChallenges.length === 0 && completedChallenges.length === 0 && (
        <div className="text-center py-8 text-teen-purple-500">
          <Clock className="w-12 h-12 mx-auto mb-3 opacity-50" />
          <p>Brak aktywnych wyzwań</p>
          <p className="text-sm">Sprawdź jutro!</p>
        </div>
      )}

      <div className="space-y-3">
        {activeChallenges.map((challenge, index) => (
          <motion.div
            key={challenge.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="p-4 bg-teen-purple-50 rounded-lg border border-teen-purple-200"
          >
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-teen-pink-400 rounded-full animate-pulse" />
                <span className="font-medium text-teen-purple-700">{challenge.name}</span>
              </div>
              <span className="text-sm text-teen-purple-600">+{challenge.points} pkt</span>
            </div>
            
            <p className="text-sm text-teen-purple-600 mb-3">{challenge.description}</p>
            
            <div className="flex items-center justify-between">
              <div className="flex-1 mr-3">
                <div className="w-full bg-teen-purple-200 rounded-full h-2">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${(challenge.progress / challenge.target) * 100}%` }}
                    transition={{ duration: 0.5 }}
                    className="bg-gradient-to-r from-teen-pink-400 to-teen-purple-400 h-2 rounded-full"
                  />
                </div>
              </div>
              <span className="text-sm text-teen-purple-600">
                {challenge.progress}/{challenge.target}
              </span>
            </div>
          </motion.div>
        ))}

        {completedChallenges.map((challenge, index) => (
          <motion.div
            key={challenge.id}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: index * 0.1 }}
            className="p-4 bg-teen-mint-50 rounded-lg border border-teen-mint-200"
          >
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center space-x-2">
                <CheckCircle className="w-4 h-4 text-teen-mint-500 fill-current" />
                <span className="font-medium text-teen-mint-700 line-through">{challenge.name}</span>
              </div>
              <span className="text-sm text-teen-mint-600">+{challenge.points} pkt</span>
            </div>
            
            <p className="text-sm text-teen-mint-600 mb-3">{challenge.description}</p>
            
            <div className="flex items-center justify-between">
              <div className="flex-1 mr-3">
                <div className="w-full bg-teen-mint-200 rounded-full h-2">
                  <div className="bg-teen-mint-400 h-2 rounded-full w-full" />
                </div>
              </div>
              <span className="text-sm text-teen-mint-600">
                {challenge.target}/{challenge.target} ✓
              </span>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Summary */}
      {state.challenges.length > 0 && (
        <div className="mt-4 pt-4 border-t border-teen-purple-200">
          <div className="flex justify-between text-sm">
            <span className="text-teen-purple-600">Ukończone dzisiaj:</span>
            <span className="text-teen-purple-700 font-medium">
              {completedChallenges.length}/{state.challenges.length}
            </span>
          </div>
          <div className="flex justify-between text-sm mt-1">
            <span className="text-teen-purple-600">Punkty do zdobycia:</span>
            <span className="text-teen-purple-700 font-medium">
              {activeChallenges.reduce((sum, c) => sum + c.points, 0)} pkt
            </span>
          </div>
        </div>
      )}
    </motion.div>
  )
} 