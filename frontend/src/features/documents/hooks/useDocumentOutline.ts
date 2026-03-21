import { useQuery } from '@tanstack/react-query'
import { api } from '@/lib/api'
import type { DocumentOutlineResponse } from '../types/document'

const documentKeys = {
  outline: (projectId: number) => ['projects', projectId, 'documents', 'outline'] as const,
  sectionContent: (projectId: number, sectionId: string) =>
    ['projects', projectId, 'documents', 'sections', sectionId, 'content'] as const,
}

export function useDocumentOutline(projectId: number) {
  return useQuery({
    queryKey: documentKeys.outline(projectId),
    queryFn: () => api.get<DocumentOutlineResponse>(`/projects/${projectId}/documents/outline`),
    refetchInterval: 15000,
    staleTime: 10000,
  })
}

export { documentKeys }
