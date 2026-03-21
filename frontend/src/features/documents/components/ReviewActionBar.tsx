import { useState } from 'react'
import { CheckCircle2, MessageSquare, XCircle } from 'lucide-react'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { useReviewContext } from '../context/ReviewContext'
import type { SectionReview } from '../types/verification'

interface ReviewActionBarProps {
  sectionId: string
}

export function ReviewActionBar({ sectionId }: ReviewActionBarProps) {
  const ctx = useReviewContext()
  if (!ctx) return null

  const { reviews, setReview } = ctx
  const existing = reviews[sectionId]

  const [activeAction, setActiveAction] = useState<SectionReview['status'] | null>(
    existing?.status ?? null
  )
  const [feedback, setFeedback] = useState<string>(existing?.feedback ?? '')
  const [saved, setSaved] = useState(false)

  function handleGoedkeuren() {
    setActiveAction('goedgekeurd')
    setReview(sectionId, 'goedgekeurd', '')
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  function handleOpmerking() {
    setActiveAction('opmerking')
  }

  function handleAfwijzen() {
    setActiveAction('afgewezen')
  }

  function handleSave() {
    if (!activeAction || activeAction === 'goedgekeurd') return
    setReview(sectionId, activeAction, feedback)
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  const showTextarea = activeAction === 'opmerking' || activeAction === 'afgewezen'

  return (
    <div className="mt-4 pt-4 border-t border-border">
      {/* Action buttons */}
      <div className="flex items-center gap-2 flex-wrap">
        <Button
          variant="outline"
          size="sm"
          onClick={handleGoedkeuren}
          className={cn(
            activeAction === 'goedgekeurd' &&
              'bg-green-500/10 text-green-600 border-green-500/30 hover:bg-green-500/20'
          )}
        >
          <CheckCircle2 className="h-4 w-4" />
          Goedkeuren
        </Button>

        <Button
          variant="outline"
          size="sm"
          onClick={handleOpmerking}
          className={cn(
            activeAction === 'opmerking' &&
              'bg-amber-500/10 text-amber-600 border-amber-500/30 hover:bg-amber-500/20'
          )}
        >
          <MessageSquare className="h-4 w-4" />
          Opmerking toevoegen
        </Button>

        <Button
          variant="outline"
          size="sm"
          onClick={handleAfwijzen}
          className={cn(
            activeAction === 'afgewezen' &&
              'bg-red-500/10 text-red-600 border-red-500/30 hover:bg-red-500/20'
          )}
        >
          <XCircle className="h-4 w-4" />
          Afwijzen
        </Button>

        {saved && (
          <span className="text-sm text-muted-foreground">Opgeslagen</span>
        )}
      </div>

      {/* Feedback textarea — only for Opmerking / Afwijzen */}
      {showTextarea && (
        <div className="mt-3 space-y-2">
          <Textarea
            value={feedback}
            onChange={(e) => setFeedback(e.target.value)}
            placeholder="Beschrijf uw opmerking of reden voor afwijzing..."
            className="text-sm"
          />
          <Button size="sm" onClick={handleSave}>
            Opslaan
          </Button>
        </div>
      )}
    </div>
  )
}
