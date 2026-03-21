import { useQuery } from '@tanstack/react-query'
import { api } from '@/lib/api'
import type { SectionContentResponse } from '../types/document'
import { documentKeys } from './useDocumentOutline'

export function useSectionContent(projectId: number, sectionId: string, enabled: boolean = true) {
  return useQuery({
    queryKey: documentKeys.sectionContent(projectId, sectionId),
    queryFn: () => api.get<SectionContentResponse>(
      `/projects/${projectId}/documents/sections/${encodeURIComponent(sectionId)}/content`
    ),
    enabled,
    refetchInterval: 30000,
    staleTime: 25000,
  })
}
