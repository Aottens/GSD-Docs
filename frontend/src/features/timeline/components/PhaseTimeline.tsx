import { Skeleton } from '@/components/ui/skeleton'
import { PhaseNode } from './PhaseNode'
import { PhasePopover } from './PhasePopover'
import { usePhaseTimeline } from '../hooks/usePhaseStatus'

interface PhaseTimelineProps {
  projectId: number
  onNavigateToDocs?: () => void
}

/**
 * Horizontal timeline bar showing all project phases
 * Compact, always visible above workspace content
 */
export function PhaseTimeline({ projectId, onNavigateToDocs }: PhaseTimelineProps) {
  const { data, isLoading, error } = usePhaseTimeline(projectId)

  if (isLoading) {
    return (
      <div className="border-b bg-background py-2 px-4">
        <div className="flex items-center gap-2 overflow-x-auto">
          {[1, 2, 3, 4, 5].map((i) => (
            <Skeleton key={i} className="h-16 w-20 shrink-0" />
          ))}
        </div>
      </div>
    )
  }

  if (error || !data) {
    return (
      <div className="border-b bg-background py-2 px-4">
        <p className="text-xs text-muted-foreground">
          Fase tijdlijn kon niet worden geladen
        </p>
      </div>
    )
  }

  return (
    <div className="border-b bg-background py-2 px-4 shrink-0">
      <div className="flex items-center gap-1 overflow-x-auto">
        {data.phases.map((phase, index) => (
          <div key={phase.number} className="flex items-center shrink-0">
            <PhasePopover phase={phase} projectId={projectId} onNavigateToDocs={onNavigateToDocs}>
              <PhaseNode phase={phase} />
            </PhasePopover>

            {index < data.phases.length - 1 && (
              <div className="h-px w-6 bg-border mx-1" />
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
