import { CheckCircle2, Circle, Check } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { cn } from '@/lib/utils'
import { usePhaseTimeline } from '../hooks/usePhaseStatus'
import { CliCommandBlock } from './CliCommandBlock'

interface FaseringTabProps {
  projectId: number
}

/**
 * Full detailed phase view showing all phases with expanded details
 * Vertical card layout with progress checklists and CLI command display
 */
export function FaseringTab({ projectId }: FaseringTabProps) {
  const { data, isLoading, error } = usePhaseTimeline(projectId)

  const getStatusStyle = (status: string) => {
    if (status === 'completed') {
      return { color: 'text-green-500', bg: 'bg-green-500/10', Icon: CheckCircle2 }
    }
    if (['discussed', 'planned', 'written', 'verified', 'reviewed'].includes(status)) {
      return { color: 'text-amber-500', bg: 'bg-amber-500/10', Icon: CheckCircle2 }
    }
    return { color: 'text-muted-foreground', bg: 'bg-muted', Icon: Circle }
  }

  if (isLoading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <Skeleton key={i} className="h-48 w-full" />
        ))}
      </div>
    )
  }

  if (error || !data) {
    return (
      <div className="flex items-center justify-center h-full">
        <p className="text-muted-foreground">Fase informatie kon niet worden geladen</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="space-y-2">
        <h2 className="text-2xl font-bold">Fasering</h2>
        <p className="text-muted-foreground">
          Overzicht van alle project fases met status
        </p>
      </div>

      <div className="space-y-4">
        {data.phases.map((phase) => {
          const statusStyle = getStatusStyle(phase.status)
          const Icon = statusStyle.Icon

          return (
            <Card key={phase.number} className="overflow-hidden">
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex items-start gap-3">
                    <div className={cn('p-2 rounded-lg', statusStyle.bg)}>
                      <Icon className={cn('h-5 w-5', statusStyle.color)} />
                    </div>
                    <div className="space-y-1">
                      <CardTitle className="text-lg">
                        Fase {phase.number}: {phase.name}
                      </CardTitle>
                      <p className="text-sm text-muted-foreground">{phase.goal}</p>
                    </div>
                  </div>
                  <Badge variant="outline" className="shrink-0">
                    {phase.sub_status || 'Nog te starten'}
                  </Badge>
                </div>
              </CardHeader>

              <CardContent className="space-y-4">
                {/* Progress Checklist */}
                <div>
                  <p className="text-sm font-medium mb-2">Voortgang:</p>
                  <div className="grid grid-cols-2 gap-2">
                    <div className="flex items-center gap-2 text-sm">
                      {phase.has_context ? (
                        <Check className="h-4 w-4 text-green-500" />
                      ) : (
                        <Circle className="h-4 w-4 text-muted-foreground" />
                      )}
                      <span className={phase.has_context ? '' : 'text-muted-foreground'}>
                        CONTEXT.md
                      </span>
                    </div>
                    <div className="flex items-center gap-2 text-sm">
                      {phase.has_plans ? (
                        <Check className="h-4 w-4 text-green-500" />
                      ) : (
                        <Circle className="h-4 w-4 text-muted-foreground" />
                      )}
                      <span className={phase.has_plans ? '' : 'text-muted-foreground'}>
                        PLAN.md
                      </span>
                    </div>
                    <div className="flex items-center gap-2 text-sm">
                      {phase.has_content ? (
                        <Check className="h-4 w-4 text-green-500" />
                      ) : (
                        <Circle className="h-4 w-4 text-muted-foreground" />
                      )}
                      <span className={phase.has_content ? '' : 'text-muted-foreground'}>
                        Content
                      </span>
                    </div>
                    <div className="flex items-center gap-2 text-sm">
                      {phase.has_verification ? (
                        <Check className="h-4 w-4 text-green-500" />
                      ) : (
                        <Circle className="h-4 w-4 text-muted-foreground" />
                      )}
                      <span className={phase.has_verification ? '' : 'text-muted-foreground'}>
                        Verificatie
                      </span>
                    </div>
                    <div className="flex items-center gap-2 text-sm">
                      {phase.has_review ? (
                        <Check className="h-4 w-4 text-green-500" />
                      ) : (
                        <Circle className="h-4 w-4 text-muted-foreground" />
                      )}
                      <span className={phase.has_review ? '' : 'text-muted-foreground'}>
                        Beoordeling
                      </span>
                    </div>
                  </div>
                </div>

                {/* CLI Command */}
                {phase.cli_command && (
                  <div>
                    <p className="text-sm font-medium mb-2">Volgende stap:</p>
                    <CliCommandBlock command={phase.cli_command} />
                  </div>
                )}
              </CardContent>
            </Card>
          )
        })}
      </div>
    </div>
  )
}
