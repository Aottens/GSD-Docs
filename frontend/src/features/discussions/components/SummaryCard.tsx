import { useState } from 'react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import type { Decision } from '../types/conversation'

interface SummaryCardProps {
  topic: string
  decisions: Decision[]
  onConfirm: () => void
  onEdit: (index: number, newValue: string) => void
  onAdd: (decision: string) => void
}

export function SummaryCard({ topic, decisions, onConfirm, onEdit, onAdd }: SummaryCardProps) {
  const [editingIndex, setEditingIndex] = useState<number | null>(null)
  const [editValue, setEditValue] = useState('')
  const [addingNew, setAddingNew] = useState(false)
  const [newDecision, setNewDecision] = useState('')

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

  const handleAddSave = () => {
    if (newDecision.trim()) {
      onAdd(newDecision.trim())
      setNewDecision('')
      setAddingNew(false)
    }
  }

  return (
    <Card className="p-4 space-y-4 max-w-2xl">
      <div>
        <h4 className="font-semibold text-lg">{topic}</h4>
        <p className="text-sm text-muted-foreground">Samenvatting van beslissingen</p>
      </div>

      <div className="space-y-2">
        {decisions.map((decision, idx) => (
          <div key={idx} className="p-3 rounded-lg border bg-background space-y-2">
            {editingIndex === idx ? (
              <>
                <Textarea
                  value={editValue}
                  onChange={(e) => setEditValue(e.target.value)}
                  className="min-h-[60px]"
                  autoFocus
                />
                <div className="flex gap-2">
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
              <>
                <p className="text-sm">{decision.decision}</p>
                {decision.reasoning && (
                  <p className="text-xs text-muted-foreground italic">
                    Redenering: {decision.reasoning}
                  </p>
                )}
              </>
            )}
          </div>
        ))}

        {addingNew && (
          <div className="p-3 rounded-lg border border-dashed space-y-2">
            <Textarea
              value={newDecision}
              onChange={(e) => setNewDecision(e.target.value)}
              placeholder="Voeg een nieuwe beslissing toe..."
              className="min-h-[60px]"
              autoFocus
            />
            <div className="flex gap-2">
              <Button size="sm" onClick={handleAddSave}>
                Toevoegen
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={() => {
                  setAddingNew(false)
                  setNewDecision('')
                }}
              >
                Annuleren
              </Button>
            </div>
          </div>
        )}
      </div>

      <div className="flex gap-2 pt-2">
        <Button onClick={onConfirm} className="flex-1">
          Bevestigen
        </Button>
        <Button variant="outline" onClick={() => handleEditStart(0)} disabled={decisions.length === 0}>
          Aanpassen
        </Button>
        <Button variant="outline" onClick={() => setAddingNew(true)}>
          Toevoegen
        </Button>
      </div>
    </Card>
  )
}
