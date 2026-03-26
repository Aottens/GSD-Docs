import { useRef, useEffect } from 'react'
import { toast } from 'sonner'
import { useDocumentOutline } from './useDocumentOutline'
import type { DocumentOutlineResponse, OutlineNode } from '../types/document'

function countWithContent(nodes: OutlineNode[]): number {
  return nodes.reduce((acc, n) => {
    const self = n.status === 'written' || n.status === 'verified' ? 1 : 0
    return acc + self + countWithContent(n.children ?? [])
  }, 0)
}

function fingerprint(data: DocumentOutlineResponse): string {
  return `${data.sections.length}:${countWithContent(data.sections)}`
}

export function useDocumentOutlineWithNotification(projectId: number) {
  const query = useDocumentOutline(projectId)
  const prevRef = useRef<string | undefined>(undefined)

  useEffect(() => {
    if (!query.data) return
    const curr = fingerprint(query.data)
    if (prevRef.current === undefined) {
      prevRef.current = curr
      return
    }
    if (prevRef.current !== curr) {
      toast.info('Documentstructuur bijgewerkt', {
        description: 'Nieuwe secties beschikbaar na CLI schrijffase.',
      })
      prevRef.current = curr
    }
  }, [query.data])

  return query
}
