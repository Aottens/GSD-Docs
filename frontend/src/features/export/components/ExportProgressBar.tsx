import { Circle, Loader2, CheckCircle2, XCircle } from 'lucide-react'
import { Progress } from '@/components/ui/progress'
import type { PipelineStage } from '@/types/export'

interface ExportProgressBarProps {
  stages: PipelineStage[]
}

function StepIcon({ status }: { status: PipelineStage['status'] }) {
  if (status === 'running') {
    return <Loader2 className="h-4 w-4 text-blue-500 animate-spin" />
  }
  if (status === 'done') {
    return <CheckCircle2 className="h-4 w-4 text-green-500" />
  }
  if (status === 'error') {
    return <XCircle className="h-4 w-4 text-destructive" />
  }
  return <Circle className="h-4 w-4 text-muted-foreground" />
}

export function ExportProgressBar({ stages }: ExportProgressBarProps) {
  const completedCount = stages.filter(s => s.status === 'done').length
  const progressValue = (completedCount / stages.length) * 100

  return (
    <div className="flex flex-col gap-3">
      <Progress value={progressValue} className="transition-all duration-300" />
      <div className="flex items-center justify-between gap-2">
        {stages.map(stage => (
          <div key={stage.step} className="flex items-center gap-1.5 flex-1">
            <StepIcon status={stage.status} />
            <span
              className={`text-sm ${
                stage.status === 'running'
                  ? 'font-medium'
                  : stage.status === 'done'
                  ? 'text-muted-foreground'
                  : 'text-muted-foreground'
              }`}
            >
              {stage.name}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}
