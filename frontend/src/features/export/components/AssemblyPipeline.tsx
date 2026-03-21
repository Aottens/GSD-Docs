import { ChevronRight } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Alert, AlertTitle, AlertDescription } from '@/components/ui/alert'
import { useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import { useAssemblyStream } from '../hooks/useAssemblyStream'
import { usePandocStatus, useAssemblyReadiness } from '../hooks/useExportApi'
import { PipelineStage } from './PipelineStage'
import { ExportProgressBar } from './ExportProgressBar'
import { useEffect } from 'react'

interface AssemblyPipelineProps {
  projectId: number
  mode: string
  language: string
}

export function AssemblyPipeline({ projectId, mode, language }: AssemblyPipelineProps) {
  const queryClient = useQueryClient()
  const { stages, isRunning, start, cancel, completedFilename } = useAssemblyStream(projectId)
  const { data: pandocStatus } = usePandocStatus(projectId)
  const { data: readiness } = useAssemblyReadiness(projectId, mode)

  const isFinalBlocked =
    mode === 'final' &&
    readiness?.unreviewed_phases &&
    readiness.unreviewed_phases.length > 0

  // When export completes, show toast and invalidate version history
  useEffect(() => {
    if (completedFilename) {
      toast.success('Export voltooid. Uw document staat klaar om te downloaden.')
      queryClient.invalidateQueries({ queryKey: ['export-versions', projectId] })
    }
  }, [completedFilename, projectId, queryClient])

  const handleStart = () => {
    start({ mode, language })
  }

  const allDone = stages.every(s => s.status === 'done')
  const downloadFilename = completedFilename

  return (
    <div className="flex flex-col gap-4">
      <h2 className="text-xl font-semibold">FDS Exportpijplijn</h2>

      {pandocStatus && !pandocStatus.installed && (
        <Alert variant="destructive">
          <AlertTitle>Pandoc niet gevonden</AlertTitle>
          <AlertDescription>
            <span>Installeer Pandoc om DOCX te exporteren:</span>
            <code className="block mt-2 bg-muted rounded px-1.5 py-0.5 font-mono text-sm">
              brew install pandoc
            </code>
          </AlertDescription>
        </Alert>
      )}

      {isFinalBlocked && (
        <Alert variant="default">
          <AlertTitle>Definitief exporteren niet mogelijk</AlertTitle>
          <AlertDescription>
            Alle fases moeten zijn gereviewd voor een definitieve export. Open het
            Documenten-tabblad om de review te voltooien.
          </AlertDescription>
        </Alert>
      )}

      {/* Pipeline stages */}
      <div className="flex flex-row gap-4 items-stretch">
        {/* Stage 1: Samenstellen */}
        <PipelineStage
          stage={{ ...stages[0], name: 'Samenstellen' }}
          actionLabel="Samenstellen starten"
          onAction={handleStart}
          disabled={isRunning || !!isFinalBlocked || (pandocStatus !== undefined && !pandocStatus.installed)}
        />
        <div className="flex items-center">
          <ChevronRight className="h-5 w-5 text-muted-foreground" />
        </div>
        {/* Stage 2: Exporteren */}
        <PipelineStage
          stage={{ ...stages[1], name: 'Exporteren' }}
          actionLabel="Exporteren starten"
          onAction={() => {}}
          disabled={true}
        />
        <div className="flex items-center">
          <ChevronRight className="h-5 w-5 text-muted-foreground" />
        </div>
        {/* Stage 3: Downloaden */}
        <PipelineStage
          stage={{ ...stages[2], name: 'Downloaden' }}
          actionLabel="Downloaden"
          onAction={() => {
            if (downloadFilename) {
              window.open(`/api/projects/${projectId}/export/download/${downloadFilename}`)
            }
          }}
          disabled={!allDone || !downloadFilename}
        />
      </div>

      {/* Progress bar when running */}
      {isRunning && (
        <div className="flex flex-col gap-3">
          <ExportProgressBar stages={stages} />
          <Button
            variant="destructive"
            onClick={cancel}
            className="min-h-[44px] w-fit"
          >
            Annuleren
          </Button>
        </div>
      )}
    </div>
  )
}
