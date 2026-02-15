import { useState } from 'react'
import { Send, Bot } from 'lucide-react'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'

export function ChatContextPanel() {
  const [activeTab, setActiveTab] = useState('chat')

  return (
    <div className="flex flex-col h-full bg-muted/20">
      {/* Header */}
      <div className="p-4 border-b bg-background">
        <div className="flex items-center gap-2">
          <Bot className="h-5 w-5 text-primary" />
          <h3 className="font-semibold">Assistant</h3>
        </div>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1 flex flex-col">
        <TabsList className="mx-4 mt-4">
          <TabsTrigger value="chat" className="flex-1">
            Chat
          </TabsTrigger>
          <TabsTrigger value="context" className="flex-1">
            Context
          </TabsTrigger>
        </TabsList>

        <TabsContent value="chat" className="flex-1 p-4 mt-0">
          <Card className="h-full flex items-center justify-center bg-muted/50">
            <div className="text-center p-6 max-w-sm space-y-2">
              <Bot className="h-12 w-12 mx-auto text-muted-foreground/50 mb-4" />
              <p className="text-sm text-muted-foreground">
                Chat will be available when you start a discussion phase.
              </p>
              <p className="text-xs text-muted-foreground/70">Coming in Phase 10</p>
            </div>
          </Card>
        </TabsContent>

        <TabsContent value="context" className="flex-1 p-4 mt-0">
          <Card className="h-full flex items-center justify-center bg-muted/50">
            <div className="text-center p-6 max-w-sm space-y-2">
              <p className="text-sm text-muted-foreground">
                Context documents will appear here during active phases.
              </p>
              <p className="text-xs text-muted-foreground/70">Coming in Phase 10</p>
            </div>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Input Area */}
      <div className="p-4 border-t bg-background">
        <div className="flex gap-2">
          <Input
            placeholder="Available in discussion phase..."
            disabled
            className="flex-1"
          />
          <Button size="icon" disabled>
            <Send className="h-4 w-4" />
          </Button>
        </div>
        <p className="text-xs text-muted-foreground mt-2 text-center">
          Phase 10: Discussion workflow
        </p>
      </div>
    </div>
  )
}
