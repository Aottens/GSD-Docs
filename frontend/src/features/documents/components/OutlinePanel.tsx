import { Skeleton } from '@/components/ui/skeleton'
import { OutlineNode } from './OutlineNode'
import type { OutlineNode as OutlineNodeType } from '../types/document'

interface OutlinePanelProps {
  sections: OutlineNodeType[]
  language: 'nl' | 'en'
  activeId: string | null
  onSelect: (id: string) => void
  isLoading?: boolean
  error?: boolean
}

export function OutlinePanel({
  sections,
  language,
  activeId,
  onSelect,
  isLoading,
  error,
}: OutlinePanelProps) {
  return (
    <div className="flex flex-col h-full bg-secondary/30">
      <div className="p-4 border-b">
        <h2 className="text-sm font-semibold">Documentstructuur</h2>
      </div>
      <div className="flex-1 overflow-auto p-2">
        {isLoading && (
          <div className="space-y-2">
            {[1, 2, 3, 4, 5].map(i => (
              <Skeleton key={i} className="h-8 w-full" />
            ))}
          </div>
        )}
        {error && !isLoading && (
          <p className="text-sm text-muted-foreground p-4">
            Documentstructuur kon niet worden geladen. Controleer of het project bestaat en probeer opnieuw.
          </p>
        )}
        {!isLoading && !error && sections.map(section => (
          <OutlineNode
            key={section.id}
            node={section}
            language={language}
            activeId={activeId}
            onSelect={onSelect}
            depth={0}
          />
        ))}
      </div>
    </div>
  )
}
