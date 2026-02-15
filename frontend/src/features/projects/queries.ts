import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from '@/lib/api'
import type { Project, ProjectCreate } from '@/types/project'

export function useProject(id: number | string) {
  return useQuery({
    queryKey: ['projects', id],
    queryFn: async () => {
      const response = await api.get<Project>(`/projects/${id}`)
      return response
    },
    enabled: !!id,
  })
}

export function useCreateProject() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (data: ProjectCreate) => {
      const response = await api.post<Project>('/projects/', data)
      return response
    },
    onSuccess: () => {
      // Invalidate projects list cache
      queryClient.invalidateQueries({ queryKey: ['projects'] })
    },
  })
}
