import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Check } from 'lucide-react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'

interface QuestionCardProps {
  question: string
  options?: string[]
  onAnswer: (answer: string) => void
  isActive?: boolean
}

export function QuestionCard({ question, options, onAnswer, isActive = true }: QuestionCardProps) {
  const [customAnswer, setCustomAnswer] = useState('')
  const [selectedChip, setSelectedChip] = useState<string | null>(null)
  const [submittedAnswer, setSubmittedAnswer] = useState<string | null>(null)

  const handleChipClick = (option: string) => {
    // Chip click sends message but does NOT close the card
    // Card stays open for follow-up question from AI
    setSelectedChip(option)
    onAnswer(option)
  }

  const handleCustomSubmit = () => {
    if (!customAnswer.trim()) return
    setSubmittedAnswer(customAnswer)
    onAnswer(customAnswer)
    setCustomAnswer('')
  }

  // Collapsed state when inactive (new question card arrived)
  if (!isActive) {
    const displayAnswer = submittedAnswer || selectedChip
    return (
      <Card className="p-4 space-y-3 max-w-2xl bg-muted/50">
        <div className="prose prose-sm dark:prose-invert max-w-none">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{question}</ReactMarkdown>
        </div>
        {displayAnswer && (
          <div className="border-l-2 border-primary pl-3">
            <p className="text-sm font-medium">Gekozen antwoord:</p>
            <p className="text-sm text-muted-foreground">{displayAnswer}</p>
          </div>
        )}
      </Card>
    )
  }

  // Active state - card is open for interaction
  return (
    <Card className="p-4 space-y-4 max-w-2xl">
      <div className="prose prose-sm dark:prose-invert max-w-none font-medium">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>{question}</ReactMarkdown>
      </div>

      {/* Option chips - show checkmark on selected chip */}
      {options && options.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {options.map((opt, idx) => (
            <Button
              key={idx}
              variant={selectedChip === opt ? 'default' : 'outline'}
              size="sm"
              onClick={() => handleChipClick(opt)}
              className="gap-1"
            >
              {selectedChip === opt && <Check className="h-3 w-3" />}
              {opt}
            </Button>
          ))}
        </div>
      )}

      {/* Divider */}
      <div className="flex items-center gap-2">
        <div className="flex-1 border-t" />
        <span className="text-xs text-muted-foreground">Of geef een gedetailleerd antwoord:</span>
        <div className="flex-1 border-t" />
      </div>

      {/* Freeform input - always visible */}
      <div className="space-y-2">
        <Textarea
          value={customAnswer}
          onChange={(e) => setCustomAnswer(e.target.value)}
          placeholder="Beschrijf de specificaties..."
          className="min-h-[80px]"
        />
        <Button
          onClick={handleCustomSubmit}
          disabled={!customAnswer.trim()}
          className="w-full"
        >
          Verstuur
        </Button>
      </div>
    </Card>
  )
}
