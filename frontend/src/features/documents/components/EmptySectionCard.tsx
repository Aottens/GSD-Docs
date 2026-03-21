import { Copy } from 'lucide-react'
import { toast } from 'sonner'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'

interface CliCommandBlockProps {
  command: string
}

function CliCommandBlock({ command }: CliCommandBlockProps) {
  const handleCopy = async () => {
    await navigator.clipboard.writeText(command)
    toast.success('Gekopieerd!')
  }
  return (
    <div className="flex items-center gap-2 bg-muted rounded px-3 py-2">
      <code className="text-sm font-mono flex-1 text-foreground">{command}</code>
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

interface EmptySectionCardProps {
  sectionId: string
  sectionTitle: string
  status: string
  cliCommand: string | null
}

export function EmptySectionCard({ sectionId, sectionTitle, status, cliCommand }: EmptySectionCardProps) {
  return (
    <Card className="border-dashed">
      <CardContent className="py-6 space-y-4">
        <div>
          <h3 className="text-sm font-semibold">{sectionId} {sectionTitle}</h3>
          <p className="text-sm text-muted-foreground mt-1">
            {status === 'planned'
              ? 'Deze sectie is gepland maar nog niet geschreven. Voer `/doc:write-phase` uit om inhoud te genereren.'
              : 'Dit project heeft nog geen gegenereerde secties. Voer `/doc:plan-phase` uit in de CLI om te beginnen.'}
          </p>
        </div>
        {cliCommand && (
          <div>
            <p className="text-sm text-muted-foreground mb-2">Voer het volgende commando uit in de CLI:</p>
            <CliCommandBlock command={cliCommand} />
          </div>
        )}
      </CardContent>
    </Card>
  )
}
