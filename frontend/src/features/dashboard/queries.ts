import { useQuery } from '@tanstack/react-query'
import { api } from '@/lib/api'
import type { Project, ProjectListResponse } from '@/types/project'
import type { DashboardTab, SortOption } from './types'

interface UseProjectsParams {
  status?: DashboardTab
  search?: string
  sortBy?: SortOption
  sortOrder?: 'asc' | 'desc'
  skip?: number
  limit?: number
}

export function useProjects(params: UseProjectsParams = {}) {
  const { status, search, sortBy, sortOrder, skip, limit } = params

  // Build query string
  const queryParams = new URLSearchParams()

  if (status && status !== 'all') {
    queryParams.append('status', status)
  }

  if (search) {
    queryParams.append('search', search)
  }

  if (sortBy) {
    queryParams.append('sort_by', sortBy)
  }

  if (sortOrder) {
    queryParams.append('sort_order', sortOrder)
  }

  if (skip !== undefined) {
    queryParams.append('skip', skip.toString())
  }

  if (limit !== undefined) {
    queryParams.append('limit', limit.toString())
  }

  const queryString = queryParams.toString()
  const url = `/projects${queryString ? '?' + queryString : ''}`

  return useQuery({
    queryKey: ['projects', params],
    queryFn: () => api.get<ProjectListResponse>(url),
  })
}

export function useRecentProjects() {
  return useQuery({
    queryKey: ['projects', 'recent'],
    queryFn: () => api.get<Project[]>('/projects/recent'),
  })
}
