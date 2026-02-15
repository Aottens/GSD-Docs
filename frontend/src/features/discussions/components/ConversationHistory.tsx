import { MessageSquare, Calendar, CheckCircle2, Clock } from 'lucide-react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { useConversationHistory } from '../hooks/useConversationHistory'

interface ConversationHistoryProps {
  projectId: string
  onViewConversation: (id: number) => void
  onStartRevision: (id: number) => void
}

export function ConversationHistory({
  projectId,
  onViewConversation,
  onStartRevision,
}: ConversationHistoryProps) {
  const { data: conversations, isLoading } = useConversationHistory(projectId)

  if (isLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-32 w-full" />
        <Skeleton className="h-32 w-full" />
        <Skeleton className="h-32 w-full" />
      </div>
    )
  }

  if (!conversations || conversations.length === 0) {
    return (
      <div className="flex items-center justify-center py-16">
        <div className="text-center space-y-3">
          <MessageSquare className="h-12 w-12 mx-auto text-muted-foreground/50" />
          <p className="text-muted-foreground">Nog geen gesprekken gevoerd</p>
          <p className="text-sm text-muted-foreground/70">
            Start een discussiefase om uw eerste gesprek te beginnen
          </p>
        </div>
      </div>
    )
  }

  // Group by phase
  const groupedByPhase = conversations.reduce((acc, conv) => {
    const key = conv.phase_number
    if (!acc[key]) acc[key] = []
    acc[key].push(conv)
    return acc
  }, {} as Record<number, typeof conversations>)

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold">Gesprekken</h2>
        <p className="text-muted-foreground">Alle discussies met de AI assistent</p>
      </div>

      {Object.entries(groupedByPhase).map(([phaseNumber, convs]) => (
        <div key={phaseNumber} className="space-y-3">
          <h3 className="text-lg font-medium">Fase {phaseNumber}</h3>
          <div className="space-y-3">
            {convs.map((conv) => (
              <Card key={conv.id} className="p-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1 space-y-2">
                    <div className="flex items-center gap-2">
                      <h4 className="font-medium">
                        {conv.title || `Gesprek Fase ${conv.phase_number}`}
                      </h4>
                      {conv.status === 'active' && (
                        <Badge variant="default" className="gap-1">
                          <Clock className="h-3 w-3" />
                          Actief
                        </Badge>
                      )}
                      {conv.status === 'completed' && (
                        <Badge variant="secondary" className="gap-1">
                          <CheckCircle2 className="h-3 w-3" />
                          Voltooid
                        </Badge>
                      )}
                      {conv.parent_id && (
                        <Badge variant="outline">Bijgewerkt</Badge>
                      )}
                    </div>

                    <div className="flex items-center gap-4 text-sm text-muted-foreground">
                      <div className="flex items-center gap-1">
                        <Calendar className="h-3 w-3" />
                        {new Date(conv.created_at).toLocaleDateString('nl-NL')}
                      </div>
                      <div className="flex items-center gap-1">
                        <MessageSquare className="h-3 w-3" />
                        {conv.message_count} berichten
                      </div>
                    </div>
                  </div>

                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => onViewConversation(conv.id)}
                    >
                      Bekijken
                    </Button>
                    {conv.status === 'completed' && (
                      <Button
                        variant="default"
                        size="sm"
                        onClick={() => onStartRevision(conv.id)}
                      >
                        Bijwerken
                      </Button>
                    )}
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}
