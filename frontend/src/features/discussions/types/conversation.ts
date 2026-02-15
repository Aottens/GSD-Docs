export interface Conversation {
  id: number
  project_id: number
  phase_number: number
  status: 'active' | 'completed' | 'archived'
  title: string | null
  summary_data: Decision[] | null
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
  message_type: 'text' | 'question_card' | 'summary_card' | 'topic_selection' | 'decision_edit'
  metadata_json: MessageMetadata | null
  timestamp: string
}

export interface Decision {
  topic: string
  decision: string
  reasoning?: string
}

export interface MessageMetadata {
  question?: string
  options?: string[]
  selected_topics?: string[]
  decision?: Decision
  attachments?: string[]
}

export interface StreamEvent {
  event: 'message_delta' | 'message_complete' | 'question_card' | 'summary_card' | 'error' | 'done'
  data: {
    delta?: string
    accumulated?: string
    final?: string
    question?: string
    options?: string[]
    decision?: Decision
    error?: string
  }
}
