export type ProjectType = 'A' | 'B' | 'C' | 'D'
export type Language = 'nl' | 'en'
export type ProjectStatus = 'active' | 'completed' | 'archived'

export interface Project {
  id: number
  name: string
  type: ProjectType
  language: Language
  status: ProjectStatus
  current_phase: number
  progress: number
  created_at: string
  updated_at: string
  last_accessed_at: string | null
}

export interface ProjectCreate {
  name: string
  type: ProjectType
  language: Language
}

export interface ProjectUpdate {
  name?: string
  type?: ProjectType
  language?: Language
  status?: ProjectStatus
  current_phase?: number
  progress?: number
}

export interface ProjectListResponse {
  projects: Project[]
  total: number
}
