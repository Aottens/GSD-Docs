import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from '@/lib/api'
import type { SdsResults } from '@/types/sds'

export function useSdsResults(projectId: number) {
  return useQuery({
    queryKey: ['sds-results', projectId],
    queryFn: () => api.get<SdsResults>(`/projects/${projectId}/sds/results`),
    enabled: !!projectId,
  })
}

export function useSdsScaffold(projectId: number) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: () => api.post<SdsResults>(`/projects/${projectId}/sds/scaffold`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sds-results', projectId] })
    },
  })
}
