import { motion } from 'motion/react'
import type { TypeInfo } from '../types'

interface TypeCardProps {
  type: TypeInfo
  isSelected: boolean
  onClick: () => void
}

const typeColors: Record<string, string> = {
  A: 'border-t-blue-500',
  B: 'border-t-emerald-500',
  C: 'border-t-amber-500',
  D: 'border-t-rose-500',
}

export function TypeCard({ type, isSelected, onClick }: TypeCardProps) {
  return (
    <motion.button
      type="button"
      onClick={onClick}
      className={`
        relative p-6 rounded-lg border-2 border-t-4 text-left transition-all
        ${typeColors[type.id] || 'border-t-gray-500'}
        ${
          isSelected
            ? 'ring-2 ring-primary bg-primary/5 border-primary'
            : 'border-border bg-card hover:shadow-md'
        }
      `}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      transition={{ type: 'spring', stiffness: 300, damping: 20 }}
    >
      <div className="space-y-3">
        <div className="flex items-center gap-3">
          <div
            className={`
            w-10 h-10 rounded-md flex items-center justify-center font-bold text-lg
            ${type.id === 'A' && 'bg-blue-500/10 text-blue-500'}
            ${type.id === 'B' && 'bg-emerald-500/10 text-emerald-500'}
            ${type.id === 'C' && 'bg-amber-500/10 text-amber-500'}
            ${type.id === 'D' && 'bg-rose-500/10 text-rose-500'}
          `}
          >
            {type.id}
          </div>
          <h3 className="font-semibold text-lg">{type.title}</h3>
        </div>
        <p className="text-sm text-muted-foreground leading-relaxed">{type.description}</p>
        <p className="text-sm text-muted-foreground/80 italic">Example: {type.example}</p>
      </div>
    </motion.button>
  )
}
