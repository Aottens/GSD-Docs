import { useQuery } from '@tanstack/react-query'
import { api } from '@/lib/api'
import type { ExportVersionList, AssemblyReadiness, PandocStatus } from '@/types/export'

export function useExportVersions(projectId: number) {
  return useQuery({
    queryKey: ['export-versions', projectId],
    queryFn: () => api.get<ExportVersionList>('/projects/' + projectId + '/export/versions'),
    enabled: !!projectId,
  })
}

export function useAssemblyReadiness(projectId: number, mode: string) {
  return useQuery({
    queryKey: ['export-readiness', projectId, mode],
    queryFn: () =>
      api.get<AssemblyReadiness>('/projects/' + projectId + '/export/readiness?mode=' + mode),
    enabled: !!projectId,
  })
}

export function usePandocStatus(projectId: number) {
  return useQuery({
    queryKey: ['pandoc-status', projectId],
    queryFn: () => api.get<PandocStatus>('/projects/' + projectId + '/export/pandoc-status'),
    enabled: !!projectId,
    staleTime: 5 * 60 * 1000,
  })
}
