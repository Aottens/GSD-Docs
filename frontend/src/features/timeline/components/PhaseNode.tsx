import { CheckCircle2, Circle } from 'lucide-react'
import { cn } from '@/lib/utils'
import type { PhaseStatus } from '../types/phase'

interface PhaseNodeProps {
  phase: PhaseStatus
}

/**
 * Compact phase node for horizontal timeline
 * Shows status icon, phase number, and sub-status badge
 * Wrapped in PhasePopover's PopoverTrigger for click interaction
 */
export function PhaseNode({ phase }: PhaseNodeProps) {
  // Determine status category and color
  const getStatusStyle = () => {
    if (phase.status === 'completed') {
      return { iconColor: 'text-green-500', Icon: CheckCircle2 }
    }
    if (['discussed', 'planned', 'written', 'verified', 'reviewed'].includes(phase.status)) {
      return { iconColor: 'text-amber-500', Icon: CheckCircle2 }
    }
    return { iconColor: 'text-muted-foreground', Icon: Circle }
  }

  const { iconColor, Icon } = getStatusStyle()

  return (
    <button
      type="button"
      className="flex flex-col items-center gap-1 h-auto py-2 px-3 rounded-md hover:bg-accent transition-colors"
    >
      <Icon className={cn('h-5 w-5', iconColor)} />
      <span className="text-xs font-medium whitespace-nowrap">Fase {phase.number}</span>
      {phase.sub_status && (
        <span className="text-[10px] text-muted-foreground max-w-[80px] truncate">
          {phase.sub_status}
        </span>
      )}
    </button>
  )
}
