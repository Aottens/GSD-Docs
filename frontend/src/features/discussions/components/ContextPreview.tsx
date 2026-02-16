import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { FileText, ChevronLeft, Edit3, AlertCircle } from 'lucide-react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Textarea } from '@/components/ui/textarea'
import { Alert, AlertDescription } from '@/components/ui/alert'

interface ContextPreviewProps {
  content: string
  lineCount: number
  onEdit: (content: string) => void
  onFinalize: (editedContent?: string) => void
  onBack: () => void
}

export function ContextPreview({
  content,
  lineCount,
  onEdit,
  onFinalize,
  onBack,
}: ContextPreviewProps) {
  const [isEditMode, setIsEditMode] = useState(false)
  const [editedContent, setEditedContent] = useState(content)

  const handleToggleEdit = () => {
    if (isEditMode) {
      // Exiting edit mode - apply changes
      onEdit(editedContent)
    }
    setIsEditMode(!isEditMode)
  }

  const handleFinalize = () => {
    // Pass edited content if it differs from original
    const hasChanges = editedContent !== content
    onFinalize(hasChanges ? editedContent : undefined)
  }

  const showWarning = lineCount > 100

  return (
    <div className="flex flex-col h-full overflow-hidden">
      {/* Header */}
      <div className="p-4 border-b shrink-0 space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <FileText className="h-5 w-5 text-primary" />
            <h3 className="font-semibold">CONTEXT.md Preview</h3>
            <Badge variant="secondary">{lineCount} regels</Badge>
          </div>
          <Button variant="ghost" size="icon" onClick={onBack}>
            <ChevronLeft className="h-4 w-4" />
          </Button>
        </div>

        {showWarning && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              Let op: {lineCount} regels (doel: max 100)
            </AlertDescription>
          </Alert>
        )}
      </div>

      {/* Preview/Edit Content */}
      <div className="flex-1 overflow-auto p-4">
        {isEditMode ? (
          <Textarea
            value={editedContent}
            onChange={(e) => setEditedContent(e.target.value)}
            className="w-full h-full min-h-[400px] font-mono text-sm resize-none"
            placeholder="CONTEXT.md content..."
          />
        ) : (
          <Card className="p-6">
            <div className="prose prose-sm dark:prose-invert max-w-none">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
            </div>
          </Card>
        )}
      </div>

      {/* Action Buttons */}
      <div className="p-4 border-t shrink-0 flex gap-2">
        <Button variant="ghost" onClick={onBack} className="flex-1">
          Terug naar gesprek
        </Button>
        <Button
          variant="secondary"
          onClick={handleToggleEdit}
          className="flex-1 gap-2"
        >
          <Edit3 className="h-4 w-4" />
          {isEditMode ? 'Voorvertoning' : 'Bewerken'}
        </Button>
        <Button onClick={handleFinalize} className="flex-1">
          Bevestig &amp; bewaar
        </Button>
      </div>
    </div>
  )
}
