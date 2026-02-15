export type FileScope = 'shared' | 'project'
export type UploadStatus = 'pending' | 'uploading' | 'validating' | 'done' | 'error'

export interface FileMetadata {
  id: number
  uuid: string
  original_filename: string
  safe_filename: string
  mime_type: string
  size_bytes: number
  scope: FileScope
  project_id: number | null
  folder_id: number | null
  overrides_file_id: number | null
  uploaded_at: string
  uploaded_by: string | null
  is_deleted: boolean
  download_url: string
}

export interface FileListResponse {
  files: FileMetadata[]
  total: number
}

export interface FolderInfo {
  id: number
  name: string
  project_id: number | null
  scope: FileScope
  parent_id: number | null
  created_at: string
  file_count?: number
}

export interface UploadProgress {
  file: File
  progress: number
  status: UploadStatus
  error?: string
}
