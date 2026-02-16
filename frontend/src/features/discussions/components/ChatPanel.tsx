import { useState, useEffect } from 'react'
import { Bot, X } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import { MessageList } from './MessageList'
import { SummaryPanel } from './SummaryPanel'
import { ConversationHistory } from './ConversationHistory'
import { ChatInput } from './ChatInput'
import { useDiscussionStream } from '../hooks/useDiscussionStream'
import { useConversation } from '../hooks/useConversationHistory'
import { toast } from 'sonner'

interface ChatPanelProps {
  projectId: string
  phaseNumber: number | null
  conversationId: number | null
  onClose: () => void
}

export function ChatPanel({
  projectId,
  phaseNumber,
  conversationId,
  onClose,
}: ChatPanelProps) {
  const [activeTab, setActiveTab] = useState('chat')
  const [viewMode, setViewMode] = useState<'active' | 'readonly'>('active')
  const [deferredCount] = useState(0)

  const {
    messages,
    isStreaming,
    currentStreamedContent,
    error,
    decisions,
    completionData,
    currentTopic,
    startDiscussion,
    sendMessage,
    confirmDecision,
    rejectDecision,
    addDecisionNote,
  } = useDiscussionStream()

  // Load conversation if conversationId provided
  const { data: conversationData } = useConversation(
    projectId,
    conversationId || 0
  )

  useEffect(() => {
    if (error) {
      toast.error('Fout tijdens gesprek', { description: error })
    }
  }, [error])

  // Start new discussion if phaseNumber provided
  useEffect(() => {
    if (phaseNumber && !conversationId) {
      startDiscussion(projectId, phaseNumber)
    }
  }, [phaseNumber, conversationId, projectId, startDiscussion])

  // Load conversation data if viewing existing conversation
  useEffect(() => {
    if (conversationData) {
      setViewMode('readonly')
      // TODO: Load messages and decisions from conversationData
    }
  }, [conversationData])

  const handleSummaryAction = (action: 'confirm' | 'edit' | 'add', data?: string) => {
    if (action === 'confirm') {
      sendMessage('Bevestig de samenvatting')
    } else if (action === 'edit' && data) {
      sendMessage(`Pas de beslissing aan: ${data}`)
    } else if (action === 'add' && data) {
      sendMessage(`Voeg beslissing toe: ${data}`)
    }
  }

  const handleViewConversation = (id: number) => {
    // TODO: Implement view conversation
    console.log('View conversation:', id)
  }

  const handleStartRevision = (id: number) => {
    // TODO: Implement start revision
    console.log('Start revision for conversation:', id)
  }

  const isReadOnly = viewMode === 'readonly'

  return (
    <div className="flex flex-col h-full bg-background">
      {/* Header */}
      <div className="p-4 border-b shrink-0">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Bot className="h-5 w-5 text-primary" />
            <h3 className="font-semibold">Assistent</h3>
            {phaseNumber && (
              <Badge variant="outline">Fase {phaseNumber}</Badge>
            )}
            {currentTopic && (
              <Badge variant="secondary" className="ml-1">
                {currentTopic}
              </Badge>
            )}
          </div>
          <Button variant="ghost" size="icon" onClick={onClose}>
            <X className="h-4 w-4" />
          </Button>
        </div>
        {completionData && (
          <div className="mt-2 text-sm text-muted-foreground">
            {completionData.message}
          </div>
        )}
      </div>

      {/* Tabs */}
      <Tabs
        value={activeTab}
        onValueChange={setActiveTab}
        className="flex-1 flex flex-col overflow-hidden"
      >
        <TabsList className="mx-4 mt-4 shrink-0">
          <TabsTrigger value="chat" className="flex-1">
            Chat
          </TabsTrigger>
          <TabsTrigger value="decisions" className="flex-1">
            Beslissingen
          </TabsTrigger>
          <TabsTrigger value="history" className="flex-1">
            Gesprekken
          </TabsTrigger>
        </TabsList>

        {/* Chat Tab */}
        <TabsContent value="chat" className="flex-1 flex overflow-hidden mt-0">
          <div className="flex-1 flex flex-col overflow-hidden">
            <MessageList
              messages={messages}
              isStreaming={isStreaming}
              currentStreamedContent={currentStreamedContent}
              onAnswer={sendMessage}
              onSummaryAction={handleSummaryAction}
            />
            <ChatInput
              onSend={sendMessage}
              disabled={isReadOnly || isStreaming}
              placeholder={
                isReadOnly
                  ? 'Alleen-lezen modus'
                  : 'Typ uw antwoord...'
              }
            />
          </div>

          {/* Summary Panel (visible whenever there are decisions) */}
          {decisions.length > 0 && (
            <SummaryPanel
              decisions={decisions}
              deferredCount={deferredCount}
              onConfirm={confirmDecision}
              onReject={rejectDecision}
              onAddNote={addDecisionNote}
            />
          )}
        </TabsContent>

        {/* Decisions Tab */}
        <TabsContent value="decisions" className="flex-1 overflow-auto p-4 mt-0">
          {decisions.length === 0 ? (
            <div className="flex items-center justify-center h-full">
              <p className="text-muted-foreground">Nog geen beslissingen vastgelegd</p>
            </div>
          ) : (
            <div className="space-y-3">
              {decisions.map((decision, idx) => (
                <div key={idx} className="p-4 border rounded-lg space-y-2">
                  <h4 className="font-medium">{decision.topic}</h4>
                  <p className="text-sm text-muted-foreground">{decision.decision}</p>
                  {decision.reasoning && (
                    <p className="text-xs text-muted-foreground/70 italic">
                      {decision.reasoning}
                    </p>
                  )}
                </div>
              ))}
            </div>
          )}
        </TabsContent>

        {/* History Tab */}
        <TabsContent value="history" className="flex-1 overflow-auto p-4 mt-0">
          <ConversationHistory
            projectId={projectId}
            onViewConversation={handleViewConversation}
            onStartRevision={handleStartRevision}
          />
        </TabsContent>
      </Tabs>
    </div>
  )
}
