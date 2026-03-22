import { useRef, useState } from 'react'
import { CheckCircle2, Clock, Circle } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Checkbox } from '@/components/ui/checkbox'
import { useDocTypeConfig } from '@/features/projects/hooks/useSetupState'
import type { UploadProgress } from '@/features/files/types/file'

export interface DocTypeFileEntry {
  file: File
  docType: string
}

interface Step4DocTypeChecklistProps {
  projectType: string
  onFilesChanged: (entries: DocTypeFileEntry[]) => void
  onSkippedChanged: (skipped: string[]) => void
  progressMap: Map<string, UploadProgress>
}

export function Step4DocTypeChecklist({
  projectType,
  onFilesChanged,
  onSkippedChanged,
  progressMap,
}: Step4DocTypeChecklistProps) {
  const { data: docTypeConfig, isLoading } = useDocTypeConfig(projectType)
  const [entries, setEntries] = useState<DocTypeFileEntry[]>([])
  const [skipped, setSkipped] = useState<string[]>([])
  const fileInputRefs = useRef<Map<string, HTMLInputElement>>(new Map())

  const getFileInputRef = (docTypeId: string) => {
    if (!fileInputRefs.current.has(docTypeId)) {
      const input = document.createElement('input')
      input.type = 'file'
      input.multiple = true
      input.addEventListener('change', () => {
        const files = Array.from(input.files || [])
        if (files.length === 0) return
        const newEntries: DocTypeFileEntry[] = files.map((file) => ({
          file,
          docType: docTypeId,
        }))
        setEntries((prev) => {
          const updated = [...prev, ...newEntries]
          onFilesChanged(updated)
          return updated
        })
        // Reset so same file can be re-selected
        input.value = ''
      })
      fileInputRefs.current.set(docTypeId, input)
    }
    return fileInputRefs.current.get(docTypeId)!
  }

  const handleUploadClick = (docTypeId: string) => {
    getFileInputRef(docTypeId).click()
  }

  const handleSkipToggle = (docTypeId: string, checked: boolean) => {
    setSkipped((prev) => {
      const updated = checked
        ? [...prev, docTypeId]
        : prev.filter((id) => id !== docTypeId)
      onSkippedChanged(updated)
      return updated
    })
  }

  const getFilesForDocType = (docTypeId: string) =>
    entries.filter((e) => e.docType === docTypeId).map((e) => e.file)

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-semibold mb-2">Referentiedocumenten</h2>
          <p className="text-muted-foreground">
            Upload de documenten die beschikbaar zijn. Ontbrekende documenten kunt u later
            toevoegen.
          </p>
        </div>
        <Card className="p-6">
          <div className="space-y-2">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-10 bg-muted rounded animate-pulse" />
            ))}
          </div>
        </Card>
      </div>
    )
  }

  if (!docTypeConfig || docTypeConfig.length === 0) {
    return (
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-semibold mb-2">Referentiedocumenten</h2>
          <p className="text-muted-foreground">
            Upload de documenten die beschikbaar zijn. Ontbrekende documenten kunt u later
            toevoegen.
          </p>
        </div>
        <Card className="p-6">
          <p className="text-sm text-muted-foreground">
            Geen documenttypes geconfigureerd voor dit projecttype. Upload referentiedocumenten via
            de Referenties tab na aanmaken.
          </p>
        </Card>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold mb-2">Referentiedocumenten</h2>
        <p className="text-muted-foreground">
          Upload de documenten die beschikbaar zijn. Ontbrekende documenten kunt u later toevoegen.
        </p>
      </div>

      <Card className="p-6">
        <div className="space-y-2">
          {docTypeConfig.map((docType) => {
            const files = getFilesForDocType(docType.id)
            const count = files.length
            const isSkipped = skipped.includes(docType.id)
            const hasFiles = count > 0

            // Check upload progress for any file in this doc type
            const isUploading = files.some((f) => {
              const prog = progressMap.get(f.name)
              return prog?.status === 'uploading' || prog?.status === 'pending'
            })

            let StatusIcon = Circle
            let iconClass = 'text-muted-foreground'
            if (isSkipped) {
              StatusIcon = Clock
              iconClass = 'text-amber-500'
            } else if (hasFiles && !isUploading) {
              StatusIcon = CheckCircle2
              iconClass = 'text-green-500'
            }

            return (
              <div
                key={docType.id}
                className={`flex items-center gap-3 rounded-lg px-3 py-2 hover:bg-muted/50 transition-colors ${isSkipped ? 'opacity-50' : ''}`}
              >
                {/* Status icon */}
                <StatusIcon className={`h-4 w-4 shrink-0 ${iconClass}`} />

                {/* Label */}
                <span
                  className={`text-sm font-medium flex-1 ${isSkipped ? 'line-through' : ''}`}
                >
                  {docType.label}
                </span>

                {/* File count */}
                <span className="text-xs text-muted-foreground">
                  {count > 0
                    ? count === 1
                      ? '1 bestand'
                      : `${count} bestanden`
                    : '\u2014'}
                </span>

                {/* Upload button */}
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  disabled={isSkipped}
                  onClick={() => handleUploadClick(docType.id)}
                >
                  {hasFiles ? 'Toevoegen' : 'Uploaden'}
                </Button>

                {/* Niet beschikbaar toggle */}
                <div className="flex items-center gap-1.5">
                  <Checkbox
                    id={`skip-${docType.id}`}
                    checked={isSkipped}
                    onCheckedChange={(checked) =>
                      handleSkipToggle(docType.id, !!checked)
                    }
                  />
                  <label
                    htmlFor={`skip-${docType.id}`}
                    className="text-xs text-muted-foreground cursor-pointer"
                  >
                    Niet beschikbaar
                  </label>
                </div>
              </div>
            )
          })}
        </div>
      </Card>

      <div className="bg-muted/30 border border-muted rounded-lg p-4">
        <p className="text-sm text-muted-foreground">
          <strong>Tip:</strong> Bestanden worden na het aanmaken van het project geüpload. U kunt
          deze stap overslaan en later bestanden toevoegen via de Referenties sectie in het project.
        </p>
      </div>
    </div>
  )
}
