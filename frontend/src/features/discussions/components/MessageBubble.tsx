import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Check } from 'lucide-react'
import type { Message } from '../types/conversation'
import { TopicSelectionCard } from './TopicSelectionCard'
import { QuestionCard } from './QuestionCard'
import { SummaryCard } from './SummaryCard'
import { CompletionCard } from './CompletionCard'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

interface MessageBubbleProps {
  message: Message
  onAnswer?: (answer: string) => void
  onSummaryAction?: (action: 'confirm' | 'edit' | 'add', data?: string) => void
  onCompletionConfirm?: () => void
  onCompletionAddMore?: () => void
}

export function MessageBubble({
  message,
  onAnswer,
  onSummaryAction,
  onCompletionConfirm,
  onCompletionAddMore,
}: MessageBubbleProps) {
  const isUser = message.role === 'user'
  const isSystem = message.role === 'system'

  // Render TopicSelectionCard
  if (message.message_type === 'topic_selection' && message.metadata_json?.topics && onAnswer) {
    return (
      <div className="flex justify-start">
        <TopicSelectionCard
          topics={message.metadata_json.topics}
          onConfirm={(selected, discretion) => {
            const parts = selected.join(', ')
            const msg = discretion.length > 0
              ? `${parts} [beoordeling: ${discretion.join(', ')}]`
              : parts
            onAnswer(msg)
          }}
        />
      </div>
    )
  }

  // Render CompletionCard
  if (message.message_type === 'completion_card' && message.metadata_json?.completion) {
    if (!onCompletionConfirm || !onCompletionAddMore) return null
    return (
      <div className="flex justify-start">
        <CompletionCard
          completionData={message.metadata_json.completion}
          onConfirm={onCompletionConfirm}
          onAddMore={onCompletionAddMore}
        />
      </div>
    )
  }

  // Render topic boundary
  if (message.message_type === 'topic_boundary' && message.metadata_json?.topic_boundary) {
    const { topic, status } = message.metadata_json.topic_boundary
    const isStarting = status === 'starting'
    return (
      <div className="flex justify-center my-4">
        <div
          className={cn(
            'flex items-center gap-2 px-4 py-2 rounded-full border',
            isStarting
              ? 'bg-blue-50 dark:bg-blue-950/20 border-blue-200 dark:border-blue-800 text-blue-900 dark:text-blue-100'
              : 'bg-green-50 dark:bg-green-950/20 border-green-200 dark:border-green-800 text-green-900 dark:text-green-100'
          )}
        >
          {!isStarting && <Check className="h-4 w-4" />}
          <span className="text-sm font-medium">
            {isStarting ? 'Start' : 'Afgerond'}: {topic}
          </span>
        </div>
      </div>
    )
  }

  // Render check-in card
  if (message.message_type === 'check_in' && onAnswer) {
    return (
      <div className="flex justify-start">
        <Card className="p-4 space-y-3 max-w-2xl bg-blue-50 dark:bg-blue-950/20 border-blue-200 dark:border-blue-800">
          <div className="text-sm font-medium text-blue-900 dark:text-blue-100 prose prose-sm dark:prose-invert max-w-none">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content}</ReactMarkdown>
          </div>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => onAnswer('Meer vragen over dit onderwerp')}
              className="flex-1"
            >
              Meer vragen
            </Button>
            <Button
              variant="default"
              size="sm"
              onClick={() => onAnswer('Volgend onderwerp')}
              className="flex-1"
            >
              Volgend onderwerp
            </Button>
          </div>
        </Card>
      </div>
    )
  }

  // Render decision captured notification
  if (message.message_type === 'decision_captured' && message.metadata_json?.decision) {
    const decisionText = message.metadata_json.decision.decision
    const preview = decisionText.length > 50 ? decisionText.slice(0, 50) + '...' : decisionText
    return (
      <div className="flex justify-center my-2">
        <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-green-50 dark:bg-green-950/20 border border-green-200 dark:border-green-800">
          <Check className="h-3 w-3 text-green-600 dark:text-green-400" />
          <p className="text-xs text-green-800 dark:text-green-200">
            Beslissing vastgelegd: {preview}
          </p>
        </div>
      </div>
    )
  }

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
