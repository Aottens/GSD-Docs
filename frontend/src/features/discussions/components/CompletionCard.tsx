import { CheckCircle2, Check } from 'lucide-react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import type { CompletionData } from '../types/conversation'

interface CompletionCardProps {
  completionData: CompletionData
  onAddMore: () => void
  onConfirm: () => void
}

export function CompletionCard({ completionData, onAddMore, onConfirm }: CompletionCardProps) {
  return (
    <Card className="p-6 space-y-4 max-w-2xl bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-950/20 dark:to-emerald-950/20 border-green-200 dark:border-green-800">
      {/* Header */}
      <div className="flex items-start gap-3">
        <CheckCircle2 className="h-6 w-6 text-green-600 dark:text-green-400 shrink-0 mt-0.5" />
        <div className="flex-1">
          <h3 className="font-semibold text-lg text-green-900 dark:text-green-100">
            Alle geselecteerde onderwerpen zijn besproken
          </h3>
          <p className="text-sm text-green-700 dark:text-green-300 mt-1">
            {completionData.decisions_count} beslissing{completionData.decisions_count !== 1 ? 'en' : ''} vastgelegd over {completionData.topics_covered.length} onderwerp{completionData.topics_covered.length !== 1 ? 'en' : ''}
          </p>
        </div>
      </div>

      {/* Topics List */}
      <div className="space-y-2">
        <p className="text-sm font-medium text-green-900 dark:text-green-100">
          Behandelde onderwerpen:
        </p>
        <div className="space-y-1">
          {completionData.topics_covered.map((topic, idx) => (
            <div key={idx} className="flex items-center gap-2 text-sm">
              <Check className="h-4 w-4 text-green-600 dark:text-green-400 shrink-0" />
              <span className="text-green-800 dark:text-green-200">{topic}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-2 pt-2">
        <Button
          variant="outline"
          onClick={onAddMore}
          className="flex-1 border-green-300 dark:border-green-700 hover:bg-green-100 dark:hover:bg-green-900/50"
        >
          Meer toevoegen
        </Button>
        <Button
          onClick={onConfirm}
          className="flex-1 bg-green-600 hover:bg-green-700 dark:bg-green-700 dark:hover:bg-green-600"
        >
          Bevestig &amp; bekijk CONTEXT.md
        </Button>
      </div>
    </Card>
  )
}
