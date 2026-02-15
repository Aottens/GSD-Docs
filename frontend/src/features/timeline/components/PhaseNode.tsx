import { CheckCircle2, Clock, Circle } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import type { PhaseStatus } from '../types/phase'

interface PhaseNodeProps {
  phase: PhaseStatus
  onClick: () => void
}

/**
 * Compact phase node for horizontal timeline
 * Shows status icon, phase number, and sub-status badge
 */
export function PhaseNode({ phase, onClick }: PhaseNodeProps) {
  // Determine status category and color
  const getStatusStyle = () => {
    if (phase.status === 'completed') {
      return {
        iconColor: 'text-green-500',
        Icon: CheckCircle2,
      }
    }

    // In progress statuses: discussing, planning, writing, verifying, reviewing
    if (['discussing', 'planning', 'writing', 'verifying', 'reviewing'].includes(phase.status)) {
      return {
        iconColor: 'text-blue-500',
        Icon: Clock,
      }
    }

    // Intermediate completed statuses: discussed, planned, written, verified, reviewed
    if (['discussed', 'planned', 'written', 'verified', 'reviewed'].includes(phase.status)) {
      return {
        iconColor: 'text-amber-500',
        Icon: CheckCircle2,
      }
    }

    // Not started
    return {
      iconColor: 'text-muted-foreground',
      Icon: Circle,
    }
  }

  const { iconColor, Icon } = getStatusStyle()

  return (
    <Button
      variant="ghost"
      size="sm"
      onClick={onClick}
      className="flex flex-col items-center gap-1 h-auto py-2 px-3 hover:bg-accent"
    >
      <Icon className={cn('h-5 w-5', iconColor)} />
      <span className="text-xs font-medium whitespace-nowrap">Fase {phase.number}</span>
      {phase.sub_status && (
        <span className="text-[10px] text-muted-foreground max-w-[80px] truncate">
          {phase.sub_status}
        </span>
      )}
    </Button>
  )
}
