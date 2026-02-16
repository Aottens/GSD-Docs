import { useState, useCallback, useRef } from 'react'
import type { Message, StreamEvent, Decision, CompletionData } from '../types/conversation'
import { api } from '@/lib/api'

interface UseDiscussionStreamReturn {
  messages: Message[]
  isStreaming: boolean
  currentStreamedContent: string
  error: string | null
  decisions: Decision[]
  completionData: CompletionData | null
  currentTopic: string | null
  contextPreview: { content: string; lineCount: number } | null
  isPreviewMode: boolean
  startDiscussion: (projectId: string, phaseNumber: number) => Promise<void>
  sendMessage: (content: string, attachments?: string[]) => Promise<void>
  confirmDecision: (index: number) => void
  rejectDecision: (index: number) => void
  addDecisionNote: (index: number, note: string) => void
  previewContext: () => Promise<void>
  finalizeDiscussion: (editedContent?: string) => Promise<void>
  addMoreTopics: () => void
  exitPreviewMode: () => void
}

export function useDiscussionStream(): UseDiscussionStreamReturn {
  const [messages, setMessages] = useState<Message[]>([])
  const [isStreaming, setIsStreaming] = useState(false)
  const [currentStreamedContent, setCurrentStreamedContent] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [conversationId, setConversationId] = useState<number | null>(null)
  const [decisions, setDecisions] = useState<Decision[]>([])
  const [completionData, setCompletionData] = useState<CompletionData | null>(null)
  const [currentTopic, setCurrentTopic] = useState<string | null>(null)
  const [contextPreview, setContextPreview] = useState<{ content: string; lineCount: number } | null>(null)
  const [isPreviewMode, setIsPreviewMode] = useState(false)
  const projectIdRef = useRef<string | null>(null)
  const abortControllerRef = useRef<AbortController | null>(null)

  const startDiscussion = useCallback(async (projectId: string, phaseNumber: number) => {
    try {
      setError(null)
      projectIdRef.current = projectId
      // Create new conversation
      const conversation = await api.post<{ id: number; message_count: number }>(
        `/projects/${projectId}/discussions`,
        { phase_number: phaseNumber }
      )
      setConversationId(conversation.id)

      // Load initial messages (system + topic selection)
      const msgs = await api.get<Message[]>(
        `/projects/${projectId}/discussions/${conversation.id}/messages`
      )
      // Filter out system messages, show only assistant messages
      setMessages(msgs.filter((m: Message) => m.role !== 'system'))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start discussion')
    }
  }, [])

  const sendMessage = useCallback(async (content: string, attachments?: string[]) => {
    if (!conversationId) {
      setError('No active conversation')
      return
    }

    try {
      setError(null)
      setIsStreaming(true)
      setCurrentStreamedContent('')

      // Cancel any existing stream
      if (abortControllerRef.current) {
        abortControllerRef.current.abort()
      }
      abortControllerRef.current = new AbortController()

      // Add user message immediately
      const userMessage: Message = {
        id: Date.now(), // temporary ID
        conversation_id: conversationId,
        role: 'user',
        content,
        message_type: 'text',
        metadata_json: attachments ? { attachments } : null,
        timestamp: new Date().toISOString(),
      }
      setMessages((prev) => [...prev, userMessage])

      // Use fetch with ReadableStream for POST with body
      const response = await fetch(`/api/projects/${projectIdRef.current}/discussions/${conversationId}/messages/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ content, attachments }),
        signal: abortControllerRef.current.signal,
      })

      if (!response.ok) {
        throw new Error(`Stream failed: ${response.statusText}`)
      }

      const reader = response.body?.getReader()
      if (!reader) {
        throw new Error('No response body')
      }

      const decoder = new TextDecoder()
      let buffer = ''
      let accumulated = ''

      // Read SSE events from stream
      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6)
            if (data === '[DONE]') {
              setIsStreaming(false)
              setCurrentStreamedContent('')
              break
            }

            try {
              const event: StreamEvent = JSON.parse(data)

              if (event.event === 'message_delta' && event.data.delta) {
                accumulated += event.data.delta
                setCurrentStreamedContent(accumulated)
              } else if (event.event === 'message_complete' && event.data.final) {
                // Add complete assistant message
                const assistantMessage: Message = {
                  id: Date.now(),
                  conversation_id: conversationId,
                  role: 'assistant',
                  content: event.data.final,
                  message_type: 'text',
                  metadata_json: null,
                  timestamp: new Date().toISOString(),
                }
                setMessages((prev) => [...prev, assistantMessage])
                accumulated = ''
                setCurrentStreamedContent('')
              } else if (event.event === 'question_card') {
                // Add question card message
                const questionMessage: Message = {
                  id: Date.now(),
                  conversation_id: conversationId,
                  role: 'assistant',
                  content: event.data.question || '',
                  message_type: 'question_card',
                  metadata_json: {
                    question: event.data.question,
                    options: event.data.options,
                  },
                  timestamp: new Date().toISOString(),
                }
                setMessages((prev) => [...prev, questionMessage])
              } else if (event.event === 'summary_card') {
                // Add summary card message
                const summaryMessage: Message = {
                  id: Date.now(),
                  conversation_id: conversationId,
                  role: 'assistant',
                  content: 'Samenvatting',
                  message_type: 'summary_card',
                  metadata_json: {
                    decision: event.data.decision,
                  },
                  timestamp: new Date().toISOString(),
                }
                setMessages((prev) => [...prev, summaryMessage])
              } else if (event.event === 'decision_captured') {
                // Add decision to decisions state
                if (event.data.decision) {
                  setDecisions((prev) => [...prev, event.data.decision!])
                  // Also add a summary_card message to chat
                  const summaryMessage: Message = {
                    id: Date.now(),
                    conversation_id: conversationId,
                    role: 'assistant',
                    content: `Beslissing vastgelegd: ${event.data.decision.decision}`,
                    message_type: 'summary_card',
                    metadata_json: {
                      decision: event.data.decision,
                    },
                    timestamp: new Date().toISOString(),
                  }
                  setMessages((prev) => [...prev, summaryMessage])
                }
              } else if (event.event === 'topic_boundary') {
                // Update current topic and add visual boundary message
                if (event.data.topic_boundary) {
                  setCurrentTopic(event.data.topic_boundary.topic)
                  const boundaryMessage: Message = {
                    id: Date.now(),
                    conversation_id: conversationId,
                    role: 'assistant',
                    content: `${event.data.topic_boundary.status === 'starting' ? 'Start' : 'Afgerond'}: ${event.data.topic_boundary.topic}`,
                    message_type: 'topic_boundary',
                    metadata_json: {
                      topic_boundary: event.data.topic_boundary,
                    },
                    timestamp: new Date().toISOString(),
                  }
                  setMessages((prev) => [...prev, boundaryMessage])
                }
              } else if (event.event === 'completion_card') {
                // Set completion data and add completion card message
                if (event.data.completion) {
                  setCompletionData(event.data.completion)
                  const completionMessage: Message = {
                    id: Date.now(),
                    conversation_id: conversationId,
                    role: 'assistant',
                    content: event.data.completion.message,
                    message_type: 'completion_card',
                    metadata_json: {
                      completion: event.data.completion,
                    },
                    timestamp: new Date().toISOString(),
                  }
                  setMessages((prev) => [...prev, completionMessage])
                }
              } else if (event.event === 'check_in') {
                // Add check-in message to chat
                const checkInMessage: Message = {
                  id: Date.now(),
                  conversation_id: conversationId,
                  role: 'assistant',
                  content: event.data.final || 'Hoe gaat het tot nu toe?',
                  message_type: 'check_in',
                  metadata_json: null,
                  timestamp: new Date().toISOString(),
                }
                setMessages((prev) => [...prev, checkInMessage])
              } else if (event.event === 'error') {
                setError(event.data.error || 'Unknown error')
                setIsStreaming(false)
              } else if (event.event === 'done') {
                setIsStreaming(false)
                setCurrentStreamedContent('')
              }
            } catch (parseError) {
              console.error('Failed to parse SSE event:', parseError)
            }
          }
        }
      }
    } catch (err) {
      if (err instanceof Error && err.name === 'AbortError') {
        // Ignore abort errors
        return
      }
      setError(err instanceof Error ? err.message : 'Failed to send message')
      setIsStreaming(false)
      setCurrentStreamedContent('')
    }
  }, [conversationId])

  const confirmDecision = useCallback((index: number) => {
    setDecisions((prev) =>
      prev.map((d, i) => (i === index ? { ...d, confirmed: true } : d))
    )
  }, [])

  const rejectDecision = useCallback((index: number) => {
    const rejectedDecision = decisions[index]
    if (rejectedDecision) {
      // Remove decision from list
      setDecisions((prev) => prev.filter((_, i) => i !== index))
      // Send message to reopen the question
      sendMessage(`[Beslissing afgewezen] ${rejectedDecision.question}`)
    }
  }, [decisions, sendMessage])

  const addDecisionNote = useCallback((index: number, note: string) => {
    setDecisions((prev) =>
      prev.map((d, i) => (i === index ? { ...d, notes: note } : d))
    )
  }, [])

  const previewContext = useCallback(async () => {
    if (!conversationId || !projectIdRef.current) {
      setError('No active conversation')
      return
    }

    try {
      setError(null)
      const response = await api.post<{ content: string; line_count: number }>(
        `/projects/${projectIdRef.current}/discussions/${conversationId}/preview-context`,
        {}
      )
      setContextPreview({
        content: response.content,
        lineCount: response.line_count,
      })
      setIsPreviewMode(true)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to preview context')
    }
  }, [conversationId])

  const finalizeDiscussion = useCallback(async (editedContent?: string) => {
    if (!conversationId || !projectIdRef.current) {
      setError('No active conversation')
      return
    }

    try {
      setError(null)
      await api.post(
        `/projects/${projectIdRef.current}/discussions/${conversationId}/finalize`,
        editedContent ? { edited_content: editedContent } : {}
      )

      // Add final system message
      const finalMessage: Message = {
        id: Date.now(),
        conversation_id: conversationId,
        role: 'system',
        content: 'Bespreking afgerond. CONTEXT.md opgeslagen.',
        message_type: 'text',
        metadata_json: null,
        timestamp: new Date().toISOString(),
      }
      setMessages((prev) => [...prev, finalMessage])

      // Exit preview mode and show readonly view
      setIsPreviewMode(false)
      setContextPreview(null)

      // Show toast with next step suggestion
      const { toast } = await import('sonner')
      toast.success('Bespreking afgerond', {
        description: 'Volgende stap: Planning',
        action: {
          label: 'Start planning',
          onClick: () => {
            // This will be handled by the ChatPanel component
            console.log('Navigate to planning')
          },
        },
      })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to finalize discussion')
    }
  }, [conversationId])

  const addMoreTopics = useCallback(() => {
    sendMessage('Meer toevoegen')
  }, [sendMessage])

  const exitPreviewMode = useCallback(() => {
    setIsPreviewMode(false)
  }, [])

  return {
    messages,
    isStreaming,
    currentStreamedContent,
    error,
    decisions,
    completionData,
    currentTopic,
    contextPreview,
    isPreviewMode,
    startDiscussion,
    sendMessage,
    confirmDecision,
    rejectDecision,
    addDecisionNote,
    previewContext,
    finalizeDiscussion,
    addMoreTopics,
    exitPreviewMode,
  }
}
