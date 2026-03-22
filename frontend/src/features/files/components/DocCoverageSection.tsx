import { useState } from 'react'
import { CheckCircle2, Clock, Circle, ChevronDown } from 'lucide-react'
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible'
import { Skeleton } from '@/components/ui/skeleton'
import { useSetupState } from '@/features/projects/hooks/useSetupState'
import type { DocTypeEntry } from '@/types/setupState'

interface DocCoverageSectionProps {
  projectId: number
}

function DocTypeRow({ entry }: { entry: DocTypeEntry }) {
  return (
    <div className="flex items-center gap-3 rounded-lg px-3 py-2">
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
  )
}

export function DocCoverageSection({ projectId }: DocCoverageSectionProps) {
  const [open, setOpen] = useState(false)
  const { data, isLoading } = useSetupState(projectId)

  // Don't render if no doc types available
  if (!isLoading && (!data || !data.doc_types || data.doc_types.length === 0)) {
    return null
  }

  const hasPresent = data?.doc_types?.some((dt) => dt.status === 'present') ?? false

  return (
    <Collapsible open={open} onOpenChange={setOpen}>
      <CollapsibleTrigger className="flex items-center justify-between w-full py-2">
        <h3 className="font-semibold text-lg">Document dekking</h3>
        <ChevronDown
          className="h-4 w-4 transition-transform"
          style={{ transform: open ? 'rotate(180deg)' : 'rotate(0deg)' }}
        />
      </CollapsibleTrigger>

      <CollapsibleContent>
        {isLoading ? (
          <div className="space-y-2 py-2">
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-10 w-full" />
          </div>
        ) : (
          <div className="py-2">
            <div className="space-y-1">
              {data?.doc_types?.map((entry) => (
                <DocTypeRow key={entry.id} entry={entry} />
              ))}
            </div>
            {hasPresent && (
              <p className="text-sm text-muted-foreground mt-3">
                Nieuw document toegevoegd — voer{' '}
                <code className="font-mono">/doc:discuss-phase N</code> uit om opnieuw te
                analyseren.
              </p>
            )}
          </div>
        )}
      </CollapsibleContent>
    </Collapsible>
  )
}
