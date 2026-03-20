import { useState } from 'react'
import { Check, Copy, AlertTriangle, ShieldCheck } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover'
import { toast } from 'sonner'
import type { PhaseStatus } from '../types/phase'
import { usePhaseContextFiles } from '../hooks/usePhaseStatus'

interface PhasePopoverProps {
  phase: PhaseStatus
  projectId: number
  children: React.ReactNode
}

function CliCommandBlock({ command }: { command: string }) {
  const handleCopy = async () => {
    await navigator.clipboard.writeText(command)
    toast.success('Gekopieerd!')
  }

  return (
    <div className="flex items-center gap-2 bg-muted rounded px-3 py-2">
      <code className="text-xs font-mono flex-1 text-foreground">{command}</code>
      <Button
        variant="ghost"
        size="icon"
        className="h-6 w-6 shrink-0"
        onClick={handleCopy}
        title="Kopieer naar klembord"
      >
        <Copy className="h-3 w-3" />
      </Button>
    </div>
  )
}

export function PhasePopover({ phase, projectId, children }: PhasePopoverProps) {
  const [isOpen, setIsOpen] = useState(false)
  const { data: contextData } = usePhaseContextFiles(
    projectId,
    phase.number,
    isOpen && (phase.has_context || phase.has_verification)
  )

  const getStatusDisplay = () => {
    if (phase.sub_status) {
      return phase.sub_status
    }
    return 'Nog te starten'
  }

  return (
    <Popover open={isOpen} onOpenChange={setIsOpen}>
      <PopoverTrigger asChild>
        {children}
      </PopoverTrigger>
      <PopoverContent className="w-80" align="center">
        <div className="space-y-4">
          {/* Header */}
          <div>
            <h4 className="font-semibold text-sm mb-1">
              Fase {phase.number}: {phase.name}
            </h4>
            <p className="text-xs text-muted-foreground">{phase.goal}</p>
          </div>

          {/* Status */}
          <div>
            <p className="text-xs font-medium mb-2">Status: {getStatusDisplay()}</p>

            {/* Progress indicators */}
            <div className="space-y-1 text-xs">
              {phase.has_context && (
                <div className="flex items-center gap-2 text-muted-foreground">
                  <Check className="h-3 w-3 text-green-500" />
                  <span>CONTEXT.md aanwezig</span>
                </div>
              )}
              {phase.has_plans && (
                <div className="flex items-center gap-2 text-muted-foreground">
                  <Check className="h-3 w-3 text-green-500" />
                  <span>PLAN.md aanwezig</span>
                </div>
              )}
              {phase.has_content && (
                <div className="flex items-center gap-2 text-muted-foreground">
                  <Check className="h-3 w-3 text-green-500" />
                  <span>Content geschreven</span>
                </div>
              )}
              {phase.has_verification && (
                <div className="flex items-center gap-2 text-muted-foreground">
                  <Check className="h-3 w-3 text-green-500" />
                  <span>Geverifieerd</span>
                </div>
              )}
              {phase.has_review && (
                <div className="flex items-center gap-2 text-muted-foreground">
                  <Check className="h-3 w-3 text-green-500" />
                  <span>Beoordeeld</span>
                </div>
              )}
            </div>
          </div>

          {/* CLI Command */}
          {phase.cli_command && (
            <div>
              <p className="text-xs font-medium mb-2">Volgende stap:</p>
              <CliCommandBlock command={phase.cli_command} />
            </div>
          )}

          {/* Verification Score */}
          {contextData?.has_verification && contextData.verification_score && (
            <div>
              <p className="text-xs font-medium mb-2">Verificatie:</p>
              <div className="flex items-center gap-2">
                <ShieldCheck className="h-4 w-4 text-green-500" />
                <span className="text-sm">{contextData.verification_score} niveaus geslaagd</span>
                {contextData.verification_gaps != null && contextData.verification_gaps > 0 && (
                  <Badge variant="outline" className="text-xs">
                    <AlertTriangle className="h-3 w-3 mr-1" />
                    {contextData.verification_gaps} gap{contextData.verification_gaps !== 1 ? 's' : ''}
                  </Badge>
                )}
              </div>
            </div>
          )}

          {/* Context Decisions */}
          {contextData?.has_context && contextData.decisions.length > 0 && (
            <div>
              <p className="text-xs font-medium mb-2">Beslissingen:</p>
              <ul className="space-y-1 text-xs text-muted-foreground max-h-32 overflow-y-auto">
                {contextData.decisions.slice(0, 5).map((decision, i) => (
                  <li key={i} className="flex gap-2">
                    <span className="shrink-0">-</span>
                    <span>{decision}</span>
                  </li>
                ))}
                {contextData.decisions.length > 5 && (
                  <li className="text-muted-foreground/60">
                    +{contextData.decisions.length - 5} meer...
                  </li>
                )}
              </ul>
            </div>
          )}
        </div>
      </PopoverContent>
    </Popover>
  )
}
