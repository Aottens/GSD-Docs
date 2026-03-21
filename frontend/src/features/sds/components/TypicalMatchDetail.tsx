import type { TypicalMatch } from '@/types/sds'

interface TypicalMatchDetailProps {
  match: TypicalMatch
}

export function TypicalMatchDetail({ match }: TypicalMatchDetailProps) {
  return (
    <div className="p-4 space-y-3 bg-muted/30 border-t">
      {match.match_detail ? (
        <>
          <div>
            <p className="text-sm text-muted-foreground">
              <span className="font-medium text-foreground">Reden:</span>{' '}
              {match.match_detail.reason}
            </p>
          </div>

          <div className="text-sm text-muted-foreground">
            I/O: {match.match_detail.io_score}/40 | Trefwoorden:{' '}
            {match.match_detail.keyword_score}/30 | Toestanden:{' '}
            {match.match_detail.state_score}/20 | Categorie:{' '}
            {match.match_detail.category_score}/10
          </div>

          {match.match_detail.closest_match !== null && (
            <div className="text-sm">
              <span className="font-medium">Dichtstbijzijnde match:</span>{' '}
              {match.match_detail.closest_match}
              {match.match_detail.closest_confidence !== null && (
                <span className="text-muted-foreground">
                  {' '}
                  ({match.match_detail.closest_confidence}%)
                </span>
              )}
            </div>
          )}

          <div className="space-y-1">
            <p className="text-sm font-medium">Verfijnen via CLI:</p>
            <code className="block bg-muted rounded px-1.5 py-0.5 text-sm font-mono break-all">
              {match.match_detail.cli_hint}
            </code>
          </div>
        </>
      ) : (
        <p className="text-sm text-muted-foreground">
          Geen typicals-catalogus beschikbaar. Voeg een CATALOG.json toe aan het project.
        </p>
      )}
    </div>
  )
}
