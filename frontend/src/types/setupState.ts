export interface DocTypeConfigEntry {
  id: string
  label: string
  required: boolean
}

export interface DocTypeEntry {
  id: string
  label: string
  required: boolean
  status: 'present' | 'missing' | 'skipped'
  file_count: number
  file_paths: string[]
}

export interface SetupStateResponse {
  project_id: number
  project_name: string
  project_type: string
  language: string
  project_dir: string
  doc_types: DocTypeEntry[]
  has_scaffolding: boolean
  next_cli_command: string | null
}
