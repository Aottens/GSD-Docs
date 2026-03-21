import { Loader2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { useSdsResults, useSdsScaffold } from '../hooks/useSdsApi'
import { TypicalsMatchTable } from './TypicalsMatchTable'

interface SdsTabProps {
  projectId: number
}

export function SdsTab({ projectId }: SdsTabProps) {
  const { data, isLoading, isError } = useSdsResults(projectId)
  const scaffold = useSdsScaffold(projectId)

  return (
    <div className="space-y-6 p-6">
      <div>
        <h2 className="text-2xl font-semibold">SDS Opbouw</h2>
        <p className="text-sm text-muted-foreground mt-1">
          Bekijk de typicals-koppeling voor dit project. Start de opbouw om uitrusting te
          matchen met catalogus-typicals.
        </p>
      </div>

      <Button
        variant="default"
        onClick={() => scaffold.mutate()}
        disabled={scaffold.isPending}
      >
        {scaffold.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
        SDS Opbouwen
      </Button>

      {isLoading && (
        <div className="space-y-2">
          {Array.from({ length: 5 }).map((_, i) => (
            <Skeleton key={i} className="h-9 w-full" />
          ))}
        </div>
      )}

      {isError && (
        <p className="text-sm text-muted-foreground">
          Gegevens konden niet worden geladen. Ververs de pagina of controleer de verbinding.
        </p>
      )}

      {!isLoading && !isError && data && (
        <>
          {data.scaffold_date !== null ? (
            <div className="space-y-4">
              <p className="text-sm text-muted-foreground">
                {data.total_modules} modules — {data.matched_count} gekoppeld,{' '}
                {data.low_confidence_count} lage overeenkomst,{' '}
                {data.unmatched_count} nieuw typical nodig
              </p>

              {!data.catalog_found && (
                <p className="text-sm text-muted-foreground">
                  Geen typicals-catalogus gevonden. Alle modules zijn gemarkeerd als
                  &quot;NIEUW TYPICAL NODIG&quot;.
                </p>
              )}

              <TypicalsMatchTable matches={data.matches} />
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">
              SDS-opbouw nog niet gestart. Klik op &quot;SDS Opbouwen&quot; om de analyse te
              starten.
            </p>
          )}
        </>
      )}
    </div>
  )
}
