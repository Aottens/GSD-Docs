import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'

interface QuestionCardProps {
  question: string
  options?: string[]
  onAnswer: (answer: string) => void
}

export function QuestionCard({ question, options, onAnswer }: QuestionCardProps) {
  const [customAnswer, setCustomAnswer] = useState('')
  const [answered, setAnswered] = useState(false)
  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null)

  const handleOptionClick = (option: string) => {
    setSelectedAnswer(option)
    setAnswered(true)
    onAnswer(option)
  }

  const handleCustomSubmit = () => {
    if (!customAnswer.trim()) return
    setSelectedAnswer(customAnswer)
    setAnswered(true)
    onAnswer(customAnswer)
  }

  if (answered) {
    return (
      <Card className="p-4 space-y-3 max-w-2xl bg-muted/50">
        <div className="prose prose-sm dark:prose-invert max-w-none">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{question}</ReactMarkdown>
        </div>
        <div className="border-l-2 border-primary pl-3">
          <p className="text-sm font-medium">Gekozen antwoord:</p>
          <p className="text-sm text-muted-foreground">{selectedAnswer}</p>
        </div>
      </Card>
    )
  }

  return (
    <Card className="p-4 space-y-4 max-w-2xl">
      <div className="prose prose-sm dark:prose-invert max-w-none font-medium">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>{question}</ReactMarkdown>
      </div>

      {/* Option chips */}
      {options && options.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {options.map((opt, idx) => (
            <Button
              key={idx}
              variant="outline"
              size="sm"
              onClick={() => handleOptionClick(opt)}
            >
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

      {/* Freeform input */}
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
