import { Card, CardContent } from '@/components/ui/card'
import { CliCommandBlock } from '@/features/timeline/components/CliCommandBlock'

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
