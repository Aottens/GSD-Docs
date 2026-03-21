import { Circle, Loader2, CheckCircle2, XCircle } from 'lucide-react'
import { Button } from '@/components/ui/button'
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from '@/components/ui/collapsible'
import type { PipelineStage as PipelineStageType } from '@/types/export'

interface PipelineStageProps {
  stage: PipelineStageType
  actionLabel: string
  onAction: () => void
  disabled: boolean
}

function StageIcon({ status }: { status: PipelineStageType['status'] }) {
  if (status === 'running') {
    return <Loader2 className="h-8 w-8 text-blue-500 animate-spin" />
  }
  if (status === 'done') {
    return <CheckCircle2 className="h-8 w-8 text-green-500" />
  }
  if (status === 'error') {
    return <XCircle className="h-8 w-8 text-destructive" />
  }
  return <Circle className="h-8 w-8 text-muted-foreground" />
}

export function PipelineStage({ stage, actionLabel, onAction, disabled }: PipelineStageProps) {
  const isError = stage.status === 'error'

  return (
    <div
      className={`bg-card border rounded-lg p-4 flex-1 flex flex-col gap-3 min-h-[120px] transition-all duration-150 ${
        isError ? 'border-destructive' : ''
      }`}
    >
      <div className="flex items-center gap-2">
        <StageIcon status={stage.status} />
      </div>
      <p className="text-sm font-semibold">{stage.name}</p>
      <div className="mt-auto flex flex-col gap-2">
        <Button
          size="sm"
          onClick={onAction}
          disabled={disabled}
          variant={stage.status === 'done' ? 'outline' : 'default'}
        >
          {actionLabel}
        </Button>
        {isError && (
          <Collapsible>
            <CollapsibleTrigger className="text-sm text-destructive text-left w-full hover:underline">
              Stap mislukt — klik voor details
            </CollapsibleTrigger>
            <CollapsibleContent>
              <div className="bg-muted rounded p-2 font-mono text-sm mt-2 whitespace-pre-wrap">
                {stage.errorMessage || 'Onbekende fout'}
              </div>
            </CollapsibleContent>
          </Collapsible>
        )}
      </div>
    </div>
  )
}
