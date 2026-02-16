import { useEffect, useRef, useState } from 'react'
import { Bot } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import type { Message } from '../types/conversation'
import { MessageBubble } from './MessageBubble'

interface MessageListProps {
  messages: Message[]
  isStreaming: boolean
  currentStreamedContent?: string
  isLoading?: boolean
  onAnswer?: (answer: string) => void
  onSummaryAction?: (action: 'confirm' | 'edit' | 'add', data?: string) => void
  onCompletionConfirm?: () => void
  onCompletionAddMore?: () => void
}

export function MessageList({
  messages,
  isStreaming,
  currentStreamedContent,
  isLoading,
  onAnswer,
  onSummaryAction,
  onCompletionConfirm,
  onCompletionAddMore,
}: MessageListProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)
  const [autoScroll, setAutoScroll] = useState(true)
  const [showNewMessageButton, setShowNewMessageButton] = useState(false)

  // Detect user scroll
  const handleScroll = () => {
    if (!containerRef.current) return

    const { scrollTop, scrollHeight, clientHeight } = containerRef.current
    const isAtBottom = scrollHeight - scrollTop - clientHeight < 50

    setAutoScroll(isAtBottom)
    setShowNewMessageButton(!isAtBottom && messages.length > 0)
  }

  // Auto-scroll only if enabled
  useEffect(() => {
    if (autoScroll && messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [messages, currentStreamedContent, autoScroll])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    setAutoScroll(true)
    setShowNewMessageButton(false)
  }

  // Loading state
  if (isLoading) {
    return (
      <div className="flex-1 p-4 space-y-4">
        <Skeleton className="h-16 w-3/4" />
        <Skeleton className="h-16 w-2/3 ml-auto" />
        <Skeleton className="h-16 w-3/4" />
      </div>
    )
  }

  // Empty state
  if (messages.length === 0 && !currentStreamedContent) {
    return (
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="text-center space-y-3">
          <Bot className="h-12 w-12 mx-auto text-muted-foreground/50" />
          <p className="text-sm text-muted-foreground">
            Start een bespreking om vragen te ontvangen
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="relative flex-1 overflow-hidden">
      <div
        ref={containerRef}
        onScroll={handleScroll}
        className="h-full overflow-y-auto p-4 space-y-4"
      >
        {messages.map((msg) => (
          <MessageBubble
            key={msg.id}
            message={msg}
            onAnswer={onAnswer}
            onSummaryAction={onSummaryAction}
            onCompletionConfirm={onCompletionConfirm}
            onCompletionAddMore={onCompletionAddMore}
          />
        ))}

        {/* Streaming indicator */}
        {isStreaming && currentStreamedContent && (
          <div className="flex justify-start">
            <div className="max-w-[80%] rounded-lg px-4 py-2 bg-muted">
              <div className="prose prose-sm dark:prose-invert max-w-none">
                {currentStreamedContent}
              </div>
              <div className="flex items-center gap-1 mt-2">
                <div className="w-2 h-2 rounded-full bg-primary animate-bounce" />
                <div className="w-2 h-2 rounded-full bg-primary animate-bounce [animation-delay:0.2s]" />
                <div className="w-2 h-2 rounded-full bg-primary animate-bounce [animation-delay:0.4s]" />
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* New message button */}
      {showNewMessageButton && (
        <Button
          onClick={scrollToBottom}
          className="absolute bottom-4 right-4 shadow-lg"
          size="sm"
        >
          Nieuw bericht ↓
        </Button>
      )}
    </div>
  )
}
