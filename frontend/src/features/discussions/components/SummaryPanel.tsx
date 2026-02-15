import { useState } from 'react'
import { Edit2 } from 'lucide-react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import type { Decision } from '../types/conversation'

interface SummaryPanelProps {
  decisions: Decision[]
  deferredCount: number
  onEdit: (index: number, newDecision: string) => void
}

export function SummaryPanel({ decisions, deferredCount, onEdit }: SummaryPanelProps) {
  const [editingIndex, setEditingIndex] = useState<number | null>(null)
  const [editValue, setEditValue] = useState('')

  const handleEditStart = (index: number) => {
    setEditingIndex(index)
    setEditValue(decisions[index].decision)
  }

  const handleEditSave = (index: number) => {
    if (editValue.trim()) {
      onEdit(index, editValue.trim())
    }
    setEditingIndex(null)
    setEditValue('')
  }

  return (
    <div className="w-72 shrink-0 border-l bg-muted/20 p-4 space-y-4">
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
              <div className="flex items-start justify-between">
                <p className="text-sm font-medium">{decision.topic}</p>
                {editingIndex !== idx && (
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-6 w-6 shrink-0"
                    onClick={() => handleEditStart(idx)}
                  >
                    <Edit2 className="h-3 w-3" />
                  </Button>
                )}
              </div>

              {editingIndex === idx ? (
                <>
                  <Textarea
                    value={editValue}
                    onChange={(e) => setEditValue(e.target.value)}
                    className="min-h-[60px] text-sm"
                    autoFocus
                    onBlur={() => handleEditSave(idx)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault()
                        handleEditSave(idx)
                      }
                      if (e.key === 'Escape') {
                        setEditingIndex(null)
                      }
                    }}
                  />
                  <div className="flex gap-2 text-xs">
                    <Button size="sm" onClick={() => handleEditSave(idx)}>
                      Opslaan
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => setEditingIndex(null)}
                    >
                      Annuleren
                    </Button>
                  </div>
                </>
              ) : (
                <p className="text-sm text-muted-foreground">{decision.decision}</p>
              )}

              {decision.reasoning && editingIndex !== idx && (
                <p className="text-xs text-muted-foreground/70 italic">
                  {decision.reasoning}
                </p>
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
