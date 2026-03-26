import { useRef, useEffect } from 'react'
import { toast } from 'sonner'
import { usePhaseTimeline } from './usePhaseStatus'
import type { PhaseTimelineData } from '../types/phase'

function fingerprint(data: PhaseTimelineData): string {
  return data.phases.map(p => `${p.number}:${p.status}`).join(',')
}

export function usePhaseTimelineWithNotification(projectId: number) {
  const query = usePhaseTimeline(projectId)
  const prevRef = useRef<string | undefined>(undefined)

  useEffect(() => {
    if (!query.data) return
    const curr = fingerprint(query.data)
    if (prevRef.current === undefined) {
      prevRef.current = curr
      return
    }
    if (prevRef.current !== curr) {
      toast.info('Fase status bijgewerkt', {
        description: 'Een of meer fases hebben een nieuwe status na CLI werk.',
      })
      prevRef.current = curr
    }
  }, [query.data])

  return query
}
