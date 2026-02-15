import { useState, useRef, type KeyboardEvent } from 'react'
import { Send, Paperclip } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'

interface ChatInputProps {
  onSend: (content: string, attachments?: string[]) => void
  disabled?: boolean
  placeholder?: string
}

export function ChatInput({
  onSend,
  disabled = false,
  placeholder = 'Typ uw antwoord...',
}: ChatInputProps) {
  const [content, setContent] = useState('')
  const [attachments, setAttachments] = useState<string[]>([])
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const handleSend = () => {
    if (!content.trim() || disabled) return
    onSend(content.trim(), attachments.length > 0 ? attachments : undefined)
    setContent('')
    setAttachments([])
  }

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleFileAttach = () => {
    // TODO: Implement file selector from project files
    // For now, placeholder functionality
    console.log('File attach clicked - to be implemented with project file selector')
  }

  return (
    <div className="border-t bg-background p-4 space-y-2">
      {attachments.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {attachments.map((file, idx) => (
            <div
              key={idx}
              className="text-xs px-2 py-1 bg-muted rounded flex items-center gap-1"
            >
              <Paperclip className="h-3 w-3" />
              {file}
              <button
                onClick={() => setAttachments(attachments.filter((_, i) => i !== idx))}
                className="ml-1 hover:text-destructive"
              >
                ×
              </button>
            </div>
          ))}
        </div>
      )}

      <div className="flex gap-2">
        <Button
          variant="outline"
          size="icon"
          onClick={handleFileAttach}
          disabled={disabled}
          className="shrink-0"
        >
          <Paperclip className="h-4 w-4" />
        </Button>

        <Textarea
          ref={textareaRef}
          value={content}
          onChange={(e) => setContent(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={disabled}
          className="min-h-[60px] max-h-[120px] resize-none"
          rows={2}
        />

        <Button
          size="icon"
          onClick={handleSend}
          disabled={disabled || !content.trim()}
          className="shrink-0"
        >
          <Send className="h-4 w-4" />
        </Button>
      </div>

      <p className="text-xs text-muted-foreground text-center">
        Druk op Enter om te versturen, Shift+Enter voor een nieuwe regel
      </p>
    </div>
  )
}
