export interface ExportVersion {
  filename: string
  doc_type: 'FDS' | 'SDS'
  mode: 'draft' | 'final'
  language: 'nl' | 'en'
  version: string
  created_at: string
  size_bytes: number
  download_url: string
}

export interface ExportVersionList {
  project_id: number
  versions: ExportVersion[]
}

export interface AssemblyReadiness {
  ready: boolean
  mode: string
  unreviewed_phases: string[]
  has_content: boolean
}

export interface PandocStatus {
  installed: boolean
  version: string | null
}

export type PipelineStageStatus = 'idle' | 'running' | 'done' | 'error'

export interface PipelineStage {
  step: number
  name: string
  status: PipelineStageStatus
  errorMessage?: string
}

export interface ExportProgressEvent {
  event: 'step_start' | 'step_done' | 'complete' | 'error' | 'cancelled'
  step: number
  name: string
  total_steps: number
  message?: string
  artifact_filename?: string
}
