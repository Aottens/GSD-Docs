import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '@/lib/api'
import type { FileMetadata, FileListResponse, FolderInfo } from '../types/file'

// Query Keys
const fileKeys = {
  projectFiles: (projectId: number, folderId?: number, fileType?: string, search?: string) =>
    ['projects', projectId, 'files', folderId, fileType, search] as const,
  sharedFiles: (folderId?: number, fileType?: string, search?: string) =>
    ['files', 'shared', folderId, fileType, search] as const,
  projectFolders: (projectId: number) => ['projects', projectId, 'folders'] as const,
  sharedFolders: () => ['files', 'shared', 'folders'] as const,
}

// Build query params
function buildQueryParams(params: Record<string, unknown>): string {
  const filtered = Object.entries(params).filter(([_, value]) => value !== undefined && value !== null)
  if (filtered.length === 0) return ''
  const searchParams = new URLSearchParams(
    filtered.map(([key, value]) => [key, String(value)])
  )
  return `?${searchParams.toString()}`
}

// Project Files Queries
export function useProjectFiles(
  projectId: number,
  folderId?: number,
  fileType?: string,
  search?: string
) {
  return useQuery({
    queryKey: fileKeys.projectFiles(projectId, folderId, fileType, search),
    queryFn: async () => {
      const params = buildQueryParams({ folder_id: folderId, file_type: fileType, search })
      return api.get<FileListResponse>(`/projects/${projectId}/files${params}`)
    },
  })
}

export function useSharedFiles(folderId?: number, fileType?: string, search?: string) {
  return useQuery({
    queryKey: fileKeys.sharedFiles(folderId, fileType, search),
    queryFn: async () => {
      const params = buildQueryParams({ folder_id: folderId, file_type: fileType, search })
      return api.get<FileListResponse>(`/files/shared${params}`)
    },
  })
}

// Folder Queries
export function useProjectFolders(projectId: number) {
  return useQuery({
    queryKey: fileKeys.projectFolders(projectId),
    queryFn: () => api.get<FolderInfo[]>(`/projects/${projectId}/folders`),
  })
}

export function useSharedFolders() {
  return useQuery({
    queryKey: fileKeys.sharedFolders(),
    queryFn: () => api.get<FolderInfo[]>('/files/shared/folders'),
  })
}

// File Mutations
export function useDeleteFile() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (fileId: number) => api.delete(`/files/${fileId}`),
    onSuccess: () => {
      // Invalidate all file queries
      queryClient.invalidateQueries({ queryKey: ['projects'] })
      queryClient.invalidateQueries({ queryKey: ['files'] })
    },
  })
}

export function useUpdateFile() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ fileId, updates }: { fileId: number; updates: Partial<FileMetadata> }) =>
      api.patch<FileMetadata>(`/files/${fileId}`, updates),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] })
      queryClient.invalidateQueries({ queryKey: ['files'] })
    },
  })
}

export function useReplaceFile() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ fileId, newFile }: { fileId: number; newFile: File }) => {
      const formData = new FormData()
      formData.append('file', newFile)
      return api.putForm<FileMetadata>(`/files/${fileId}/replace`, formData)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] })
      queryClient.invalidateQueries({ queryKey: ['files'] })
    },
  })
}

export function useOverrideFile(projectId: number) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ fileId, newFile }: { fileId: number; newFile: File }) => {
      const formData = new FormData()
      formData.append('file', newFile)
      return api.postForm<FileMetadata>(`/files/${fileId}/override`, formData)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: fileKeys.projectFiles(projectId) })
      queryClient.invalidateQueries({ queryKey: fileKeys.projectFolders(projectId) })
    },
  })
}

// Folder Mutations
export function useCreateFolder(projectId?: number) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ name, parentId }: { name: string; parentId?: number }) => {
      const url = projectId ? `/projects/${projectId}/folders` : '/files/shared/folders'
      return api.post<FolderInfo>(url, { name, parent_id: parentId })
    },
    onSuccess: () => {
      if (projectId) {
        queryClient.invalidateQueries({ queryKey: fileKeys.projectFolders(projectId) })
      } else {
        queryClient.invalidateQueries({ queryKey: fileKeys.sharedFolders() })
      }
    },
  })
}
