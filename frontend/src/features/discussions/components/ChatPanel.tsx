import { useState, useEffect } from 'react'
import { Bot, X, ArrowRight } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { MessageList } from './MessageList'
import { SummaryPanel } from './SummaryPanel'
import { ConversationHistory } from './ConversationHistory'
import { ChatInput } from './ChatInput'
import { ContextPreview } from './ContextPreview'
import { useDiscussionStream } from '../hooks/useDiscussionStream'
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
    contextPreview,
    isPreviewMode,
    startDiscussion,
    loadConversation,
    sendMessage,
    confirmDecision,
    rejectDecision,
    addDecisionNote,
    previewContext,
    finalizeDiscussion,
    addMoreTopics,
    exitPreviewMode,
  } = useDiscussionStream()

  useEffect(() => {
    if (error) {
      toast.error('Fout tijdens gesprek', { description: error })
    }
  }, [error])

  // Start new discussion if phaseNumber provided (no existing conversation)
  useEffect(() => {
    if (phaseNumber && !conversationId) {
      startDiscussion(projectId, phaseNumber)
    }
  }, [phaseNumber, conversationId, projectId, startDiscussion])

  // Load existing conversation when conversationId provided
  useEffect(() => {
    if (conversationId && projectId) {
      loadConversation(projectId, conversationId)
    }
  }, [conversationId, projectId, loadConversation])

  // Update viewMode based on completionData (set by loadConversation for completed conversations)
  useEffect(() => {
    if (completionData) {
      setViewMode('readonly')
    }
  }, [completionData])

  // Handle finalization completion
  const handleFinalize = async (editedContent?: string) => {
    await finalizeDiscussion(editedContent)
    setViewMode('readonly')
  }

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
    loadConversation(projectId, id)
    setActiveTab('chat') // Switch to chat tab to show the loaded conversation
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
          {isPreviewMode && contextPreview ? (
            <ContextPreview
              content={contextPreview.content}
              lineCount={contextPreview.lineCount}
              onEdit={() => {}} // Edit is handled locally in ContextPreview
              onFinalize={handleFinalize}
              onBack={exitPreviewMode}
            />
          ) : (
            <div className="flex-1 flex flex-col overflow-hidden">
              <MessageList
                messages={messages}
                isStreaming={isStreaming}
                currentStreamedContent={currentStreamedContent}
                onAnswer={sendMessage}
                onSummaryAction={handleSummaryAction}
                onCompletionConfirm={previewContext}
                onCompletionAddMore={addMoreTopics}
              />
              {isReadOnly ? (
                <Alert className="m-4">
                  <ArrowRight className="h-4 w-4" />
                  <AlertDescription>
                    Volgende stap: Planning
                    <Button variant="link" className="ml-2 p-0 h-auto">
                      Start planning
                    </Button>
                  </AlertDescription>
                </Alert>
              ) : (
                <ChatInput
                  onSend={sendMessage}
                  disabled={isStreaming}
                  placeholder="Typ uw antwoord..."
                />
              )}
            </div>
          )}
        </TabsContent>

        {/* Decisions Tab */}
        <TabsContent value="decisions" className="flex-1 overflow-auto mt-0">
          <SummaryPanel
            decisions={decisions}
            deferredCount={deferredCount}
            onConfirm={confirmDecision}
            onReject={rejectDecision}
            onAddNote={addDecisionNote}
          />
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
