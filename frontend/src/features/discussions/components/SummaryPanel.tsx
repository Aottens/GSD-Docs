import { useState } from 'react'
import { Check, X } from 'lucide-react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import type { Decision } from '../types/conversation'

interface SummaryPanelProps {
  decisions: Decision[]
  deferredCount: number
  onConfirm: (index: number) => void
  onReject: (index: number) => void
  onAddNote: (index: number, note: string) => void
}

export function SummaryPanel({ decisions, deferredCount, onConfirm, onReject, onAddNote }: SummaryPanelProps) {
  const [expandedNotes, setExpandedNotes] = useState<Set<number>>(new Set())
  const [noteValues, setNoteValues] = useState<Record<number, string>>({})

  const toggleNotes = (index: number) => {
    setExpandedNotes(prev => {
      const newSet = new Set(prev)
      if (newSet.has(index)) {
        newSet.delete(index)
      } else {
        newSet.add(index)
      }
      return newSet
    })
  }

  const handleNoteSave = (index: number) => {
    const note = noteValues[index] || ''
    if (note.trim()) {
      onAddNote(index, note.trim())
    }
    toggleNotes(index)
  }

  return (
    <div className="p-4 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">Beslissingen</h3>
        <Badge variant="secondary">{decisions.length}</Badge>
      </div>

      {decisions.length === 0 ? (
        <p className="text-sm text-muted-foreground text-center py-8">
          Nog geen beslissingen vastgelegd
        </p>
      ) : (
        <div className="space-y-3">
          {decisions.map((decision, idx) => (
            <Card key={idx} className="p-3 space-y-2">
              {/* Topic header */}
              <div className="flex items-start justify-between">
                <p className="text-sm font-medium text-primary">{decision.topic}</p>
                {decision.confirmed && (
                  <div className="flex items-center gap-1 text-green-600">
                    <Check className="h-4 w-4" />
                    <span className="text-xs">Bevestigd</span>
                  </div>
                )}
              </div>

              {/* Decision text */}
              <p className="text-sm text-muted-foreground">{decision.decision}</p>

              {/* Notes if present */}
              {decision.notes && (
                <p className="text-xs text-muted-foreground/70 italic border-l-2 pl-2">
                  {decision.notes}
                </p>
              )}

              {/* Action buttons (only show if not confirmed) */}
              {!decision.confirmed && (
                <div className="flex items-center gap-2 pt-1">
                  <Button
                    variant="default"
                    size="sm"
                    onClick={() => onConfirm(idx)}
                    className="flex-1"
                  >
                    <Check className="h-3 w-3 mr-1" />
                    Bevestig
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => onReject(idx)}
                    className="flex-1"
                  >
                    <X className="h-3 w-3 mr-1" />
                    Afwijzen
                  </Button>
                </div>
              )}

              {/* Add notes link (only show if not confirmed and no notes) */}
              {!decision.confirmed && !decision.notes && !expandedNotes.has(idx) && (
                <button
                  onClick={() => toggleNotes(idx)}
                  className="text-xs text-muted-foreground hover:text-foreground underline"
                >
                  Notitie toevoegen
                </button>
              )}

              {/* Notes input (expanded) */}
              {expandedNotes.has(idx) && (
                <div className="space-y-2">
                  <Textarea
                    value={noteValues[idx] || ''}
                    onChange={(e) => setNoteValues(prev => ({ ...prev, [idx]: e.target.value }))}
                    placeholder="Voeg context of notities toe..."
                    className="min-h-[60px] text-sm"
                    autoFocus
                  />
                  <div className="flex gap-2">
                    <Button size="sm" onClick={() => handleNoteSave(idx)}>
                      Opslaan
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => toggleNotes(idx)}
                    >
                      Annuleren
                    </Button>
                  </div>
                </div>
              )}
            </Card>
          ))}
        </div>
      )}

      {deferredCount > 0 && (
        <div className="pt-4 border-t">
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Uitgestelde ideeen</span>
            <Badge variant="outline">{deferredCount}</Badge>
          </div>
        </div>
      )}
    </div>
  )
}
