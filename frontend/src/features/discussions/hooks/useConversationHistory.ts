import { useQuery } from '@tanstack/react-query'
import { api } from '@/lib/api'
import type { Conversation, Message } from '../types/conversation'

// Query Keys
const conversationKeys = {
  list: (projectId: string, phaseNumber?: number) =>
    ['projects', projectId, 'conversations', phaseNumber] as const,
  detail: (projectId: string, conversationId: number) =>
    ['projects', projectId, 'conversations', conversationId] as const,
}

interface ConversationListResponse {
  conversations: Conversation[]
}

interface ConversationDetailResponse {
  conversation: Conversation
  messages: Message[]
}

export function useConversationHistory(projectId: string, phaseNumber?: number) {
  return useQuery({
    queryKey: conversationKeys.list(projectId, phaseNumber),
    queryFn: async () => {
      const params = phaseNumber ? `?phase_number=${phaseNumber}` : ''
      return api.get<ConversationListResponse>(`/projects/${projectId}/discussions${params}`)
    },
    select: (data) => data.conversations,
  })
}

export function useConversation(projectId: string, conversationId: number) {
  return useQuery({
    queryKey: conversationKeys.detail(projectId, conversationId),
    queryFn: () =>
      api.get<ConversationDetailResponse>(`/projects/${projectId}/discussions/${conversationId}`),
  })
}
