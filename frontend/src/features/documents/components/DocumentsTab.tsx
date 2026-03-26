import { useCallback, useMemo, useRef, useState } from 'react'
import { GripVerticalIcon } from 'lucide-react'
import { Skeleton } from '@/components/ui/skeleton'
import { useDocumentOutlineWithNotification } from '../hooks/useDocumentOutlineWithNotification'
import { useScrollSpy } from '../hooks/useScrollSpy'
import { ReviewProvider } from '../context/ReviewContext'
import { useVerificationData } from '../hooks/useVerificationData'
import { OutlinePanel } from './OutlinePanel'
import { ContentPanel } from './ContentPanel'
import type { OutlineNode } from '../types/document'

interface DocumentsTabProps {
  projectId: number
  language: 'nl' | 'en'
  activePhaseNumber?: number
}

const MIN_WIDTH = 180
const MAX_WIDTH = 480
const DEFAULT_WIDTH = 260

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

export function DocumentsTab({ projectId, language, activePhaseNumber }: DocumentsTabProps) {
  const { data, isLoading, error } = useDocumentOutlineWithNotification(projectId)
  const [outlineWidth, setOutlineWidth] = useState(DEFAULT_WIDTH)
  const isDragging = useRef(false)
  const containerRef = useRef<HTMLDivElement>(null)

  const phaseNumber = activePhaseNumber ?? undefined
  const { data: verificationData } = useVerificationData(
    projectId,
    phaseNumber ?? 0,
    !!phaseNumber
  )
  const phaseHasVerification = verificationData?.has_verification ?? false

  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    e.preventDefault()
    isDragging.current = true
    document.body.style.cursor = 'col-resize'
    document.body.style.userSelect = 'none'

    const onMouseMove = (ev: MouseEvent) => {
      if (!isDragging.current || !containerRef.current) return
      const containerLeft = containerRef.current.getBoundingClientRect().left
      const newWidth = Math.min(MAX_WIDTH, Math.max(MIN_WIDTH, ev.clientX - containerLeft))
      setOutlineWidth(newWidth)
    }

    const onMouseUp = () => {
      isDragging.current = false
      document.body.style.cursor = ''
      document.body.style.userSelect = ''
      document.removeEventListener('mousemove', onMouseMove)
      document.removeEventListener('mouseup', onMouseUp)
    }

    document.addEventListener('mousemove', onMouseMove)
    document.addEventListener('mouseup', onMouseUp)
  }, [])

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

  const content = (
    <div ref={containerRef} className="flex h-full overflow-hidden">
      <div style={{ width: outlineWidth, minWidth: MIN_WIDTH, maxWidth: MAX_WIDTH }} className="shrink-0 overflow-hidden">
        <OutlinePanel
          sections={data.sections}
          language={language}
          activeId={activeId}
          onSelect={scrollToSection}
        />
      </div>
      <div
        onMouseDown={handleMouseDown}
        className="relative flex w-1.5 shrink-0 items-center justify-center bg-border/50 hover:bg-border transition-colors cursor-col-resize select-none"
      >
        <div className="z-10 flex h-6 w-3.5 items-center justify-center rounded-sm border bg-border">
          <GripVerticalIcon className="size-3" />
        </div>
      </div>
      <div className="flex-1 overflow-hidden">
        <ContentPanel
          sections={data.sections}
          language={language}
          projectId={projectId}
          phaseNumber={phaseNumber}
          phaseHasVerification={phaseHasVerification}
          verificationData={verificationData ?? null}
        />
      </div>
    </div>
  )

  if (phaseNumber) {
    return (
      <ReviewProvider projectId={projectId} phaseNumber={phaseNumber}>
        {content}
      </ReviewProvider>
    )
  }
  return content
}
