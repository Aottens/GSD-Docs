import { useQuery } from '@tanstack/react-query'
import { api } from '@/lib/api'
import type { PhaseTimelineData, ContextFilesData } from '../types/phase'

// Query Keys
const phaseKeys = {
  timeline: (projectId: number) => ['projects', projectId, 'phases'] as const,
  contextFiles: (projectId: number, phaseNumber: number) =>
    ['projects', projectId, 'phases', phaseNumber, 'context-files'] as const,
}

/**
 * Fetch phase timeline data for a project
 * Refetches every 10 seconds to keep status current
 */
export function usePhaseTimeline(projectId: number) {
  return useQuery({
    queryKey: phaseKeys.timeline(projectId),
    queryFn: () => api.get<PhaseTimelineData>(`/projects/${projectId}/phases`),
    refetchInterval: 10000, // Refetch every 10 seconds
    staleTime: 5000, // Consider data stale after 5 seconds
  })
}

/**
 * Fetch context files data for a specific phase (CONTEXT.md decisions, verification score)
 * Only fetches when enabled (popover is open and phase has context/verification)
 */
export function usePhaseContextFiles(projectId: number, phaseNumber: number, enabled: boolean = true) {
  return useQuery({
    queryKey: phaseKeys.contextFiles(projectId, phaseNumber),
    queryFn: () => api.get<ContextFilesData>(`/projects/${projectId}/phases/${phaseNumber}/context-files`),
    enabled,
    staleTime: 30000, // Context files change infrequently
  })
}
