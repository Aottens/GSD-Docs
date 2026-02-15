import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import type { Message } from '../types/conversation'
import { QuestionCard } from './QuestionCard'
import { SummaryCard } from './SummaryCard'
import { cn } from '@/lib/utils'

interface MessageBubbleProps {
  message: Message
  onAnswer?: (answer: string) => void
  onSummaryAction?: (action: 'confirm' | 'edit' | 'add', data?: string) => void
}

export function MessageBubble({ message, onAnswer, onSummaryAction }: MessageBubbleProps) {
  const isUser = message.role === 'user'
  const isSystem = message.role === 'system'

  // Render QuestionCard if message has question metadata
  if (message.message_type === 'question_card' && message.metadata_json?.question && onAnswer) {
    return (
      <div className="flex justify-start">
        <QuestionCard
          question={message.metadata_json.question}
          options={message.metadata_json.options}
          onAnswer={onAnswer}
        />
      </div>
    )
  }

  // Render SummaryCard if message type is summary_card
  if (message.message_type === 'summary_card' && message.metadata_json?.decision && onSummaryAction) {
    const { decision } = message.metadata_json
    return (
      <div className="flex justify-start">
        <SummaryCard
          topic={decision.topic}
          decisions={[decision]}
          onConfirm={() => onSummaryAction('confirm')}
          onEdit={(_index: number, newValue: string) => onSummaryAction('edit', newValue)}
          onAdd={(newDecision: string) => onSummaryAction('add', newDecision)}
        />
      </div>
    )
  }

  // System messages (centered, small, italic)
  if (isSystem) {
    return (
      <div className="flex justify-center my-2">
        <p className="text-sm italic text-muted-foreground">{message.content}</p>
      </div>
    )
  }

  // Regular message bubbles
  return (
    <div className={cn('flex', isUser ? 'justify-end' : 'justify-start')}>
      <div
        className={cn(
          'max-w-[80%] rounded-lg px-4 py-2',
          isUser
            ? 'bg-primary text-primary-foreground'
            : 'bg-muted text-foreground'
        )}
      >
        <div className="prose prose-sm dark:prose-invert max-w-none">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content}</ReactMarkdown>
        </div>
        <div
          className={cn(
            'text-xs mt-1',
            isUser ? 'text-primary-foreground/70' : 'text-muted-foreground'
          )}
        >
          {new Date(message.timestamp).toLocaleTimeString('nl-NL', {
            hour: '2-digit',
            minute: '2-digit',
          })}
        </div>
      </div>
    </div>
  )
}
