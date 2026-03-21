import { useQuery } from '@tanstack/react-query'
import { api } from '@/lib/api'
import type { VerificationDetail } from '../types/verification'

const verificationKeys = {
  detail: (projectId: number, phaseNumber: number) =>
    ['projects', projectId, 'phases', phaseNumber, 'verification-detail'] as const,
}

export function useVerificationData(projectId: number, phaseNumber: number, enabled: boolean) {
  return useQuery({
    queryKey: verificationKeys.detail(projectId, phaseNumber),
    queryFn: () => api.get<VerificationDetail>(
      `/projects/${projectId}/phases/${phaseNumber}/verification-detail`
    ),
    enabled,
    refetchInterval: 30000,
    staleTime: 25000,
  })
}

export { verificationKeys }
