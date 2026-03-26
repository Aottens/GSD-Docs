import { useRef, useEffect } from 'react'
import { toast } from 'sonner'
import { useSetupState } from './useSetupState'
import type { SetupStateResponse } from '@/types/setupState'

function fingerprint(data: SetupStateResponse): string {
  return data.doc_types?.map(d => `${d.id}:${d.status}:${d.file_count}`).join(',') ?? ''
}

export function useSetupStateWithNotification(projectId: number) {
  const query = useSetupState(projectId)
  const prevRef = useRef<string | undefined>(undefined)

  useEffect(() => {
    if (!query.data) return
    const curr = fingerprint(query.data)
    if (prevRef.current === undefined) {
      prevRef.current = curr
      return
    }
    if (prevRef.current !== curr) {
      toast.info('Setup status bijgewerkt', {
        description: 'CLI heeft wijzigingen aangebracht in de projectconfiguratie.',
      })
      prevRef.current = curr
    }
  }, [query.data])

  return query
}
