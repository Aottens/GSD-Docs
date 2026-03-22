import { Copy } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { toast } from 'sonner'

export function CliCommandBlock({ command }: { command: string }) {
  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(command)
      toast.success('Gekopieerd!')
    } catch {
      toast.error('Kopieer niet beschikbaar')
    }
  }

  return (
    <div className="flex items-center gap-2 bg-muted rounded px-3 py-2">
      <code className="text-xs font-mono flex-1 text-foreground">{command}</code>
      <Button
        variant="ghost"
        size="icon"
        className="h-6 w-6 shrink-0"
        onClick={handleCopy}
        title="Kopieer naar klembord"
      >
        <Copy className="h-3 w-3" />
      </Button>
    </div>
  )
}
