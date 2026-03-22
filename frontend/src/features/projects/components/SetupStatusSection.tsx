import { CheckCircle2, Clock, Circle } from 'lucide-react'
import { Skeleton } from '@/components/ui/skeleton'
import { CliCommandBlock } from '@/features/timeline/components/CliCommandBlock'
import { useSetupState } from '../hooks/useSetupState'

interface SetupStatusSectionProps {
  projectId: number
}

export function SetupStatusSection({ projectId }: SetupStatusSectionProps) {
  const { data, isLoading, isError } = useSetupState(projectId)

  if (isLoading) {
    return (
      <div className="space-y-2">
        <Skeleton className="h-10 w-full" />
        <Skeleton className="h-10 w-full" />
        <Skeleton className="h-10 w-full" />
      </div>
    )
  }

  if (isError) {
    return (
      <p className="text-sm text-destructive">
        Setup status kon niet worden geladen. Ververs de pagina of probeer het opnieuw.
      </p>
    )
  }

  if (!data || !data.doc_types || data.doc_types.length === 0) {
    return (
      <div className="space-y-1">
        <p className="text-sm text-muted-foreground">Geen referenties geladen</p>
        <p className="text-sm text-muted-foreground">
          Upload referentiedocumenten via de wizard of de Referenties tab om setup te starten.
        </p>
      </div>
    )
  }

  return (
    <div>
      <h3 className="font-semibold text-lg mb-4">Setup status</h3>

      {/* Doc-type coverage checklist */}
      <div className="space-y-1 mb-4">
        {data.doc_types.map((entry) => (
          <div key={entry.id} className="flex items-center gap-3 rounded-lg px-3 py-2">
            {entry.status === 'present' && (
              <CheckCircle2 className="h-4 w-4 text-green-500 shrink-0" />
            )}
            {entry.status === 'skipped' && (
              <Clock className="h-4 w-4 text-amber-500 shrink-0" />
            )}
            {entry.status === 'missing' && (
              <Circle className="h-4 w-4 text-muted-foreground shrink-0" />
            )}
            <span className="text-sm font-medium flex-1">{entry.label}</span>
            <span className="text-xs text-muted-foreground">
              {entry.file_count === 0
                ? '\u2014'
                : entry.file_count === 1
                  ? '1 bestand'
                  : `${entry.file_count} bestanden`}
            </span>
          </div>
        ))}
      </div>

      {/* CLI command */}
      <p className="text-sm text-muted-foreground mb-2">Volgende stap in CLI</p>
      {data.next_cli_command ? (
        <CliCommandBlock command={data.next_cli_command} />
      ) : (
        <p className="text-sm text-muted-foreground">Alle fasen afgerond.</p>
      )}
    </div>
  )
}
