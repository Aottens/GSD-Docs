import { useMemo } from 'react'
import { ResizablePanelGroup, ResizablePanel, ResizableHandle } from '@/components/ui/resizable'
import { Skeleton } from '@/components/ui/skeleton'
import { useDocumentOutline } from '../hooks/useDocumentOutline'
import { useScrollSpy } from '../hooks/useScrollSpy'
import { OutlinePanel } from './OutlinePanel'
import { ContentPanel } from './ContentPanel'
import type { OutlineNode } from '../types/document'

interface DocumentsTabProps {
  projectId: number
  language: 'nl' | 'en'
}

function collectSectionIds(sections: OutlineNode[]): string[] {
  const ids: string[] = []
  function walk(nodes: OutlineNode[]) {
    for (const node of nodes) {
      ids.push(node.id)
      walk(node.children)
    }
  }
  walk(sections)
  return ids
}

export function DocumentsTab({ projectId, language }: DocumentsTabProps) {
  const { data, isLoading, error } = useDocumentOutline(projectId)

  const sectionIds = useMemo(
    () => data ? collectSectionIds(data.sections) : [],
    [data]
  )
  const { activeId, scrollToSection } = useScrollSpy(sectionIds)

  if (isLoading) {
    return (
      <div className="flex h-full gap-4">
        <Skeleton className="w-64 h-full" />
        <Skeleton className="flex-1 h-full" />
      </div>
    )
  }

  if (error || !data) {
    return (
      <div className="flex items-center justify-center h-full">
        <p className="text-sm text-muted-foreground">
          Documentstructuur kon niet worden geladen. Controleer of het project bestaat en probeer opnieuw.
        </p>
      </div>
    )
  }

  return (
    <ResizablePanelGroup direction="horizontal" className="h-full">
      <ResizablePanel defaultSize={25} minSize={15} maxSize={40}>
        <OutlinePanel
          sections={data.sections}
          language={language}
          activeId={activeId}
          onSelect={scrollToSection}
        />
      </ResizablePanel>
      <ResizableHandle withHandle />
      <ResizablePanel defaultSize={75}>
        <ContentPanel
          sections={data.sections}
          language={language}
          projectId={projectId}
        />
      </ResizablePanel>
    </ResizablePanelGroup>
  )
}
