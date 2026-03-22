import { useQuery } from '@tanstack/react-query'
import { api } from '@/lib/api'
import type { SetupStateResponse, DocTypeConfigEntry } from '@/types/setupState'

export function useSetupState(projectId: number) {
  return useQuery({
    queryKey: ['projects', projectId, 'setup-state'],
    queryFn: () => api.get<SetupStateResponse>(`/projects/${projectId}/setup-state`),
    refetchInterval: 5000,
    staleTime: 3000,
    enabled: !!projectId,
  })
}

export function useDocTypeConfig(projectType: string | undefined) {
  return useQuery({
    queryKey: ['doc-types', projectType],
    queryFn: () => api.get<DocTypeConfigEntry[]>(`/doc-types/${projectType}`),
    enabled: !!projectType,
    staleTime: Infinity,
  })
}
