import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { CheckCircle2, AlertTriangle, ChevronDown } from 'lucide-react'
import { cn } from '@/lib/utils'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertTitle, AlertDescription } from '@/components/ui/alert'
import {
  Collapsible,
  CollapsibleTrigger,
  CollapsibleContent,
} from '@/components/ui/collapsible'
import { StandardsBadge } from './StandardsBadge'
import type { TruthResult } from '../types/verification'

interface VerificationDetailPanelProps {
  truths: TruthResult[]
  currentCycle: number
  maxCycles: number
  isBlocked: boolean
  phaseNumber: number
}

export function VerificationDetailPanel({
  truths,
  currentCycle,
  maxCycles,
  isBlocked,
  phaseNumber,
}: VerificationDetailPanelProps) {
  const [open, setOpen] = useState(false)

  return (
    <div className="transition-all duration-150 mt-4">
      <Collapsible open={open} onOpenChange={setOpen}>
        <CollapsibleTrigger className="flex items-center gap-2 text-sm font-medium text-muted-foreground hover:text-foreground transition-colors w-full text-left py-1">
          <ChevronDown
            className={cn(
              'h-4 w-4 transition-transform duration-150',
              open ? 'rotate-0' : '-rotate-90'
            )}
          />
          Verificatieresultaten
        </CollapsibleTrigger>

        <CollapsibleContent className="mt-2 space-y-3">
          {/* Cycle badge */}
          <div className="flex items-center gap-2">
            <Badge variant="outline" className="text-xs">
              Cyclus {currentCycle}/{maxCycles}
            </Badge>
          </div>

          {/* GEBLOKKEERD alert */}
          {isBlocked && (
            <div className="space-y-2">
              <Alert variant="destructive">
                <AlertTriangle className="h-4 w-4" />
                <AlertTitle>GEBLOKKEERD</AlertTitle>
                <AlertDescription>
                  Maximaal aantal verificatiecycli bereikt. Neem contact op met de lead engineer.
                </AlertDescription>
              </Alert>
              <p className="text-sm text-muted-foreground">
                Voer uit om hiaten op te lossen:{' '}
                <code className="bg-muted rounded px-1.5 py-0.5 text-sm">
                  /doc:plan-phase {phaseNumber} --gaps
                </code>
              </p>
            </div>
          )}

          {/* Truth list */}
          <div className="space-y-0">
            {truths.map((truth, index) => (
              <div
                key={index}
                className={cn(
                  'py-3',
                  index < truths.length - 1 && 'border-b border-border'
                )}
              >
                {/* Truth header */}
                <div className="flex items-start gap-2">
                  {truth.status === 'PASS' ? (
                    <CheckCircle2 className="h-4 w-4 text-green-500 mt-0.5 shrink-0" />
                  ) : (
                    <AlertTriangle className="h-4 w-4 text-amber-500 mt-0.5 shrink-0" />
                  )}
                  <span className="text-sm">{truth.description}</span>
                </div>

                {/* GAP details */}
                {truth.status === 'GAP' && (
                  <div className="ml-6 mt-2 space-y-2">
                    {truth.failed_level && (
                      <Badge variant="secondary" className="text-xs">
                        {truth.failed_level}
                      </Badge>
                    )}
                    {truth.gap_description && (
                      <div className="text-sm text-muted-foreground">
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>
                          {truth.gap_description}
                        </ReactMarkdown>
                      </div>
                    )}

                    {/* Normen sub-section */}
                    {truth.standards_violations.length > 0 && (
                      <div className="space-y-1.5">
                        <p className="text-sm font-semibold">Normen</p>
                        <div className="flex flex-wrap gap-1.5">
                          {truth.standards_violations.map((violation, vIndex) => (
                            <StandardsBadge
                              key={vIndex}
                              reference={violation.reference}
                              text={violation.text}
                            />
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        </CollapsibleContent>
      </Collapsible>
    </div>
  )
}
