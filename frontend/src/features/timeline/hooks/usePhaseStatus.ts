import { useQuery } from '@tanstack/react-query'
import { api } from '@/lib/api'
import type { PhaseTimelineData } from '../types/phase'

// Query Keys
const phaseKeys = {
  timeline: (projectId: number) => ['projects', projectId, 'phases'] as const,
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
