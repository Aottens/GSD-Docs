import { useState, useCallback, useRef } from 'react'
import type { Message, StreamEvent } from '../types/conversation'
import { api } from '@/lib/api'

interface UseDiscussionStreamReturn {
  messages: Message[]
  isStreaming: boolean
  currentStreamedContent: string
  error: string | null
  startDiscussion: (projectId: string, phaseNumber: number) => Promise<void>
  sendMessage: (content: string, attachments?: string[]) => Promise<void>
}

export function useDiscussionStream(): UseDiscussionStreamReturn {
  const [messages, setMessages] = useState<Message[]>([])
  const [isStreaming, setIsStreaming] = useState(false)
  const [currentStreamedContent, setCurrentStreamedContent] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [conversationId, setConversationId] = useState<number | null>(null)
  const abortControllerRef = useRef<AbortController | null>(null)

  const startDiscussion = useCallback(async (projectId: string, phaseNumber: number) => {
    try {
      setError(null)
      // Create new conversation
      const conversation = await api.post<{ id: number }>(
        `/projects/${projectId}/discussions`,
        { phase_number: phaseNumber }
      )
      setConversationId(conversation.id)
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
      const response = await fetch(`/api/projects/-/discussions/${conversationId}/messages/stream`, {
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

  return {
    messages,
    isStreaming,
    currentStreamedContent,
    error,
    startDiscussion,
    sendMessage,
  }
}
