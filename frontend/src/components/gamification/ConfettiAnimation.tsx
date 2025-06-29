import { motion } from 'framer-motion'
import { useEffect, useState } from 'react'

interface ConfettiPiece {
  id: number
  x: number
  y: number
  rotation: number
  color: string
  size: number
}

interface ConfettiAnimationProps {
  isVisible: boolean
  onComplete?: () => void
}

const colors = [
  '#ec4899', // teen-pink-500
  '#a855f7', // teen-purple-500
  '#14b8a6', // teen-mint-500
  '#eab308', // teen-yellow-500
]

export default function ConfettiAnimation({ isVisible, onComplete }: ConfettiAnimationProps) {
  const [pieces, setPieces] = useState<ConfettiPiece[]>([])

  useEffect(() => {
    if (isVisible) {
      // Generate confetti pieces
      const newPieces: ConfettiPiece[] = Array.from({ length: 50 }, (_, i) => ({
        id: i,
        x: Math.random() * window.innerWidth,
        y: -20,
        rotation: Math.random() * 360,
        color: colors[Math.floor(Math.random() * colors.length)],
        size: Math.random() * 8 + 4,
      }))

      setPieces(newPieces)

      // Clean up after animation
      const timer = setTimeout(() => {
        setPieces([])
        onComplete?.()
      }, 3000)

      return () => clearTimeout(timer)
    }
  }, [isVisible, onComplete])

  if (!isVisible) return null

  return (
    <div className="fixed inset-0 pointer-events-none z-50">
      {pieces.map((piece) => (
        <motion.div
          key={piece.id}
          className="absolute"
          initial={{
            x: piece.x,
            y: piece.y,
            rotate: piece.rotation,
            scale: 0,
          }}
          animate={{
            y: window.innerHeight + 100,
            rotate: piece.rotation + 720,
            scale: [0, 1, 0.8, 0],
          }}
          transition={{
            duration: 3,
            ease: 'easeOut',
            times: [0, 0.1, 0.8, 1],
          }}
          style={{
            width: piece.size,
            height: piece.size,
            backgroundColor: piece.color,
            borderRadius: '50%',
          }}
        />
      ))}
    </div>
  )
} 