import { FileText, Upload, MessageSquare } from 'lucide-react'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { Separator } from '@/components/ui/separator'
import type { Project } from '@/types/project'

interface ProjectOverviewProps {
  project: Project
}

const typeLabels = {
  A: 'Nieuwbouw + Standaarden',
  B: 'Nieuwbouw Flex',
  C: 'Modificatie Groot',
  D: 'Modificatie Klein / TWN',
}

const typeColors = {
  A: 'bg-blue-500/10 text-blue-500 border-blue-500/20',
  B: 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20',
  C: 'bg-amber-500/10 text-amber-500 border-amber-500/20',
  D: 'bg-rose-500/10 text-rose-500 border-rose-500/20',
}

const statusLabels = {
  active: 'Actief',
  completed: 'Afgerond',
  archived: 'Gearchiveerd',
}

const statusColors = {
  active: 'bg-green-500/10 text-green-500 border-green-500/20',
  completed: 'bg-blue-500/10 text-blue-500 border-blue-500/20',
  archived: 'bg-gray-500/10 text-gray-500 border-gray-500/20',
}

export function ProjectOverview({ project }: ProjectOverviewProps) {
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('nl-NL', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    })
  }

  return (
    <div className="space-y-6">
      {/* Summary Card */}
      <Card className="p-6">
        <div className="space-y-4">
          <div>
            <h2 className="text-3xl font-bold tracking-tight mb-3">{project.name}</h2>
            <div className="flex flex-wrap gap-2">
              <Badge variant="outline" className={typeColors[project.type]}>
                Type {project.type} - {typeLabels[project.type]}
              </Badge>
              <Badge variant="outline">
                {project.language === 'nl' ? 'Nederlands (NL)' : 'Engels (EN)'}
              </Badge>
              <Badge variant="outline" className={statusColors[project.status]}>
                {statusLabels[project.status]}
              </Badge>
            </div>
          </div>

          <Separator />

          {/* Progress */}
          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground">Totale voortgang</span>
              <span className="font-medium">{project.progress}%</span>
            </div>
            <Progress value={project.progress} className="h-2" />
            <p className="text-xs text-muted-foreground">
              Huidige fase: {project.current_phase} / 17
            </p>
          </div>

          <Separator />

          {/* Metadata */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div>
              <p className="text-muted-foreground">Aangemaakt</p>
              <p className="font-medium">{formatDate(project.created_at)}</p>
            </div>
            <div>
              <p className="text-muted-foreground">Laatst gewijzigd</p>
              <p className="font-medium">{formatDate(project.updated_at)}</p>
            </div>
          </div>
        </div>
      </Card>

      {/* Quick Actions */}
      <Card className="p-6">
        <h3 className="font-semibold text-lg mb-4">Snelkoppelingen</h3>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <Button
            variant="outline"
            className="h-auto py-4 flex-col gap-2"
            disabled
            title="Beschikbaar in fase 10"
          >
            <MessageSquare className="h-5 w-5" />
            <span className="text-sm">Discussie starten</span>
            <span className="text-xs text-muted-foreground">Fase 10</span>
          </Button>
          <Button
            variant="outline"
            className="h-auto py-4 flex-col gap-2"
            disabled
            title="Beschikbaar in fase 9"
          >
            <Upload className="h-5 w-5" />
            <span className="text-sm">Referenties uploaden</span>
            <span className="text-xs text-muted-foreground">Fase 9</span>
          </Button>
          <Button
            variant="outline"
            className="h-auto py-4 flex-col gap-2"
            disabled
            title="Beschikbaar in fase 11"
          >
            <FileText className="h-5 w-5" />
            <span className="text-sm">Documenten bekijken</span>
            <span className="text-xs text-muted-foreground">Fase 11</span>
          </Button>
        </div>
      </Card>
    </div>
  )
}
