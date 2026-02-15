import { Check, MessageSquare, FileText, Pencil, CheckSquare, Eye } from 'lucide-react'
import { Button } from '@/components/ui/button'
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover'
import type { PhaseStatus } from '../types/phase'

interface PhasePopoverProps {
  phase: PhaseStatus
  onAction: (action: string, phaseNumber: number) => void
  children: React.ReactNode
}

/**
 * Inline popover showing phase status summary and action buttons
 * Only valid next actions are enabled based on available_actions
 */
export function PhasePopover({ phase, onAction, children }: PhasePopoverProps) {
  const actionConfig = {
    discuss: {
      label: 'Bespreken',
      icon: MessageSquare,
    },
    plan: {
      label: 'Plannen',
      icon: FileText,
    },
    write: {
      label: 'Schrijven',
      icon: Pencil,
    },
    verify: {
      label: 'Verifiëren',
      icon: CheckSquare,
    },
    review: {
      label: 'Beoordelen',
      icon: Eye,
    },
  }

  const getStatusDisplay = () => {
    if (phase.sub_status) {
      return phase.sub_status
    }
    return 'Nog te starten'
  }

  return (
    <Popover>
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

          {/* Actions */}
          {phase.available_actions.length > 0 && (
            <div className="space-y-2">
              <p className="text-xs font-medium">Acties:</p>
              <div className="flex flex-wrap gap-2">
                {phase.available_actions.map((action) => {
                  const config = actionConfig[action as keyof typeof actionConfig]
                  if (!config) return null

                  const Icon = config.icon
                  const isFirstAction = phase.available_actions[0] === action

                  return (
                    <Button
                      key={action}
                      size="sm"
                      variant={isFirstAction ? 'default' : 'outline'}
                      onClick={() => onAction(action, phase.number)}
                      className="gap-2"
                    >
                      <Icon className="h-3 w-3" />
                      {config.label}
                    </Button>
                  )
                })}
              </div>
            </div>
          )}

          {/* View discussion link if exists */}
          {phase.conversation_id && (
            <Button
              variant="link"
              size="sm"
              onClick={() => onAction('view-discussion', phase.number)}
              className="w-full p-0 h-auto justify-start"
            >
              Bekijk bespreking
            </Button>
          )}
        </div>
      </PopoverContent>
    </Popover>
  )
}
