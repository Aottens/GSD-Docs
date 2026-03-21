import { useState } from 'react'
import { ChevronRight, Circle, Clipboard, FileText, CheckCircle2, MessageSquare, XCircle } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Tooltip, TooltipContent, TooltipTrigger, TooltipProvider } from '@/components/ui/tooltip'
import { cn } from '@/lib/utils'
import type { OutlineNode as OutlineNodeType } from '../types/document'
import { useReviewContext } from '../context/ReviewContext'
import type { SectionReview } from '../types/verification'

function getWaveColor(wave: number): string {
  if (wave === 1) return 'bg-blue-500/10 text-blue-500 border-blue-500/20'
  if (wave === 2) return 'bg-green-500/10 text-green-500 border-green-500/20'
  if (wave === 3) return 'bg-amber-500/10 text-amber-500 border-amber-500/20'
  return 'bg-purple-500/10 text-purple-500 border-purple-500/20'
}

function getReviewIcon(reviewStatus: SectionReview['status']) {
  switch (reviewStatus) {
    case 'goedgekeurd':
      return <CheckCircle2 className="h-4 w-4 text-green-500 shrink-0" />
    case 'opmerking':
      return <MessageSquare className="h-4 w-4 text-amber-500 shrink-0" />
    case 'afgewezen':
      return <XCircle className="h-4 w-4 text-red-500 shrink-0" />
  }
}

function getReviewTooltip(reviewStatus: SectionReview['status']): string {
  switch (reviewStatus) {
    case 'goedgekeurd': return 'Goedgekeurd'
    case 'opmerking': return 'Opmerking toegevoegd'
    case 'afgewezen': return 'Afgewezen'
  }
}

function getStatusIcon(status: OutlineNodeType['status']) {
  switch (status) {
    case 'empty':
      return <Circle className="h-4 w-4 text-muted-foreground shrink-0" />
    case 'planned':
      return <Clipboard className="h-4 w-4 text-blue-500 shrink-0" />
    case 'written':
      return <FileText className="h-4 w-4 text-amber-500 shrink-0" />
    case 'verified':
      return <CheckCircle2 className="h-4 w-4 text-green-500 shrink-0" />
  }
}

interface OutlineNodeProps {
  node: OutlineNodeType
  language: 'nl' | 'en'
  activeId: string | null
  onSelect: (id: string) => void
  depth: number
}

export function OutlineNode({ node, language, activeId, onSelect, depth }: OutlineNodeProps) {
  const [isExpanded, setIsExpanded] = useState(depth <= 1)
  const hasChildren = node.children.length > 0
  const isActive = node.id === activeId

  // Null-safe context access — returns null when not inside ReviewProvider
  const ctx = useReviewContext()
  const reviewStatus = ctx?.reviews[node.id]?.status

  return (
    <div>
      <div
        className={cn(
          'flex items-center gap-1 px-2 py-1.5 rounded-md cursor-pointer min-h-[36px] hover:bg-accent',
          isActive && 'bg-accent'
        )}
        style={{ paddingLeft: `${8 + depth * 12}px` }}
        onClick={() => onSelect(node.id)}
      >
        {/* Chevron toggle */}
        <button
          className={cn(
            'h-4 w-4 shrink-0 flex items-center justify-center transition-transform',
            hasChildren ? 'opacity-100' : 'opacity-0 pointer-events-none',
            isExpanded && 'rotate-90'
          )}
          aria-label={isExpanded ? 'Sectie inklappen' : 'Sectie uitvouwen'}
          onClick={(e) => {
            e.stopPropagation()
            setIsExpanded(!isExpanded)
          }}
        >
          <ChevronRight className="h-3 w-3" />
        </button>

        {/* Status icon — review status takes precedence */}
        {reviewStatus ? (
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <span>{getReviewIcon(reviewStatus)}</span>
              </TooltipTrigger>
              <TooltipContent>{getReviewTooltip(reviewStatus)}</TooltipContent>
            </Tooltip>
          </TooltipProvider>
        ) : (
          getStatusIcon(node.status)
        )}

        {/* Title + snippet */}
        <div className="flex-1 min-w-0">
          <span className="text-sm truncate block">{node.title[language]}</span>
          {node.has_content && node.preview_snippet && (
            <span className="text-xs text-muted-foreground truncate block">
              {node.preview_snippet.slice(0, 80)}
            </span>
          )}
        </div>

        {/* Wave badge */}
        {node.has_plan && node.plan_info && (
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <Badge
                  variant="outline"
                  className={cn('text-xs shrink-0', getWaveColor(node.plan_info.wave))}
                >
                  G{node.plan_info.wave}
                </Badge>
              </TooltipTrigger>
              <TooltipContent>
                {node.plan_info.depends_on.length > 0
                  ? `Afhankelijk van: ${node.plan_info.depends_on.join(', ')}`
                  : 'Geen afhankelijkheden'}
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
        )}
      </div>

      {/* Children */}
      {hasChildren && isExpanded && (
        <div>
          {node.children.map(child => (
            <OutlineNode
              key={child.id}
              node={child}
              language={language}
              activeId={activeId}
              onSelect={onSelect}
              depth={depth + 1}
            />
          ))}
        </div>
      )}
    </div>
  )
}
