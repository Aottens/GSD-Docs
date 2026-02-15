export interface PhaseStatus {
  number: number
  name: string
  goal: string
  status: 'not_started' | 'discussing' | 'discussed' | 'planning' | 'planned' | 'writing' | 'written' | 'verifying' | 'verified' | 'reviewing' | 'reviewed' | 'completed'
  sub_status: string | null  // Dutch: Besproken, Gepland, Geschreven, Geverifieerd, Beoordeeld
  available_actions: string[]  // discuss, plan, write, verify, review
  has_context: boolean
  has_plans: boolean
  has_content: boolean
  has_verification: boolean
  has_review: boolean
  conversation_id: number | null
}

export interface PhaseTimelineData {
  project_id: number
  phases: PhaseStatus[]
}
