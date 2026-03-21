import { useState } from 'react'
import { Copy, ClipboardCheck } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useReviewContext } from '../context/ReviewContext'

interface ReviewSummaryProps {
  phaseNumber: number
}

export function ReviewSummary({ phaseNumber }: ReviewSummaryProps) {
  const ctx = useReviewContext()
  const [copied, setCopied] = useState(false)

  if (!ctx) return null

  const { reviews, exportAsJson } = ctx

  const allReviews = Object.values(reviews)
  if (allReviews.length === 0) return null

  const approved = allReviews.filter((r) => r.status === 'goedgekeurd').length
  const comments = allReviews.filter((r) => r.status === 'opmerking').length
  const rejected = allReviews.filter((r) => r.status === 'afgewezen').length

  function handleExport() {
    navigator.clipboard.writeText(exportAsJson())
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="border rounded-md p-4 mt-6 bg-muted/50">
      <p className="text-sm font-medium">
        {approved} goedgekeurd · {comments} opmerking · {rejected} afgewezen
      </p>

      <p className="text-sm text-muted-foreground mt-2">
        Genereer REVIEW.md:{' '}
        <code className="bg-muted rounded px-1.5 py-0.5 text-sm">
          /doc:review-phase {phaseNumber}
        </code>
      </p>

      <div className="mt-3">
        <Button variant="outline" size="sm" onClick={handleExport}>
          {copied ? (
            <>
              <ClipboardCheck className="h-4 w-4" />
              Gekopieerd!
            </>
          ) : (
            <>
              <Copy className="h-4 w-4" />
              Exporteer als JSON
            </>
          )}
        </Button>
      </div>
    </div>
  )
}
