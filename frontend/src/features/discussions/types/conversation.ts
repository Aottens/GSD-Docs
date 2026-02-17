export interface Conversation {
  id: number
  project_id: number
  phase_number: number
  status: 'active' | 'completed' | 'archived'
  title: string | null
  summary_data: { decisions?: Decision[] } | null
  parent_id: number | null
  created_at: string
  updated_at: string
  message_count: number
}

export interface Message {
  id: number
  conversation_id: number
  role: 'system' | 'user' | 'assistant' | 'summary'
  content: string
  message_type: 'text' | 'question_card' | 'summary_card' | 'topic_selection' | 'decision_edit' | 'completion_card' | 'topic_boundary' | 'check_in' | 'decision_captured'
  metadata_json: MessageMetadata | null
  timestamp: string
}

export interface Decision {
  topic: string
  question: string       // the question that produced this decision
  decision: string       // verbatim engineer text
  confirmed: boolean     // engineer confirmed this extraction
  notes?: string         // optional context/notes added by engineer
  timestamp: string
  reasoning?: string
}

export interface MessageMetadata {
  question?: string
  options?: string[]
  selected_topics?: string[]
  topics?: Array<{ id: string; name: string; description: string }>
  include_discretion_option?: boolean
  decision?: Decision
  attachments?: string[]
  topic_boundary?: TopicBoundaryData
  completion?: CompletionData
  decisions?: Decision[]     // topic decisions in check-in message
  all_decisions?: Decision[] // all decisions so far in check-in message
}

export type StreamEventType =
  | 'message_delta'
  | 'message_complete'
  | 'question_card'
  | 'summary_card'
  | 'decision_captured'
  | 'topic_boundary'
  | 'completion_card'
  | 'check_in'
  | 'error'
  | 'done'

export interface CompletionData {
  message: string
  decisions_count: number
  topics_covered: string[]
}

export interface TopicBoundaryData {
  topic: string
  status: 'starting' | 'complete'
}

export interface StreamEvent {
  event: StreamEventType
  data: {
    delta?: string
    accumulated?: string
    final?: string
    question?: string
    options?: string[]
    decision?: Decision
    topic_boundary?: TopicBoundaryData
    completion?: CompletionData
    error?: string
    message?: string          // for check_in events
    decisions?: Decision[]    // topic decisions at check-in
    all_decisions?: Decision[] // all decisions so far
  }
}
