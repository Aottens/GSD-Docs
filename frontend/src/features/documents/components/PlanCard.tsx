import { Card, CardHeader, CardContent, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import type { PlanInfo } from '../types/document'

function getWaveColor(wave: number): string {
  if (wave === 1) return 'bg-blue-500/10 text-blue-500 border-blue-500/20'
  if (wave === 2) return 'bg-green-500/10 text-green-500 border-green-500/20'
  if (wave === 3) return 'bg-amber-500/10 text-amber-500 border-amber-500/20'
  return 'bg-purple-500/10 text-purple-500 border-purple-500/20'
}

interface PlanCardProps {
  planInfo: PlanInfo
  sectionTitle: string
}

export function PlanCard({ planInfo, sectionTitle: _sectionTitle }: PlanCardProps) {
  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-sm font-semibold">Sectieplan</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {/* Wave assignment */}
        <div className="flex items-center gap-2">
          <span className="text-sm text-muted-foreground">Golf {planInfo.wave}</span>
          <Badge variant="outline" className={getWaveColor(planInfo.wave)}>
            G{planInfo.wave}
          </Badge>
        </div>

        {/* Dependencies */}
        <div>
          <span className="text-sm font-semibold">Afhankelijkheden</span>
          <p className="text-sm text-muted-foreground">
            {planInfo.depends_on.length > 0 ? planInfo.depends_on.join(', ') : 'Geen'}
          </p>
        </div>

        {/* Plan name */}
        <div>
          <span className="text-sm font-semibold">Plan</span>
          <p className="text-sm text-muted-foreground">{planInfo.plan_name}</p>
        </div>

        {/* Plan description (from <objective> block) — per CONTEXT.md locked decision */}
        {planInfo.description && (
          <div>
            <p className="text-sm text-muted-foreground">{planInfo.description}</p>
          </div>
        )}

        {/* Must-haves / truths (from frontmatter) — per CONTEXT.md locked decision */}
        {planInfo.truths.length > 0 && (
          <div>
            <span className="text-sm font-semibold">Vereisten</span>
            <ul className="list-disc pl-5 mt-1 space-y-0.5">
              {planInfo.truths.map((truth, i) => (
                <li key={i} className="text-sm text-muted-foreground">{truth}</li>
              ))}
            </ul>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
