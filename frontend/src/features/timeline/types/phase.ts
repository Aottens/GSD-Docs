export interface PhaseStatus {
  number: number
  name: string
  goal: string
  status: 'not_started' | 'discussed' | 'planned' | 'written' | 'verified' | 'reviewed' | 'completed'
  sub_status: string | null
  cli_command: string | null
  has_context: boolean
  has_plans: boolean
  has_content: boolean
  has_verification: boolean
  has_review: boolean
}

export interface PhaseTimelineData {
  project_id: number
  phases: PhaseStatus[]
}

export interface ContextFilesData {
  decisions: string[]
  verification_score: string | null
  verification_gaps: number | null
  verification_severity: { critical: number; major: number; minor: number } | null
  has_context: boolean
  has_verification: boolean
}
