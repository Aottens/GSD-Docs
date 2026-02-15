import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, Bot } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet'
import { ErrorMessage } from '@/components/common/ErrorMessage'
import { ProjectNavigation } from './components/ProjectNavigation'
import { ProjectOverview } from './components/ProjectOverview'
import { ChatContextPanel } from './components/ChatContextPanel'
import { useProject } from './queries'

export function ProjectWorkspace() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [activeSection, setActiveSection] = useState('overview')

  const { data: project, isLoading, error, refetch } = useProject(id || '')

  if (isLoading) {
    return (
      <div className="h-[calc(100vh-3.5rem)] p-8">
        <Skeleton className="h-8 w-64 mb-6" />
        <div className="flex gap-4 h-[calc(100%-4rem)]">
          <Skeleton className="w-64 h-full" />
          <Skeleton className="flex-1 h-full" />
        </div>
      </div>
    )
  }

  if (error || !project) {
    return (
      <div className="h-[calc(100vh-3.5rem)] p-8">
        <Button variant="ghost" onClick={() => navigate('/')} className="mb-6">
          <ArrowLeft className="mr-2 h-4 w-4" />
          Terug naar overzicht
        </Button>
        <ErrorMessage
          title="Project niet gevonden"
          message={
            error instanceof Error ? error.message : 'Het opgevraagde project kon niet worden gevonden.'
          }
          onRetry={() => refetch()}
        />
      </div>
    )
  }

  return (
    <div className="flex flex-col h-[calc(100vh-3.5rem)]">
      {/* Breadcrumb Header */}
      <div className="border-b bg-background shrink-0">
        <div className="px-4 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-sm">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => navigate('/')}
                className="h-auto p-0 hover:bg-transparent"
              >
                <span className="text-muted-foreground hover:text-foreground">Projecten</span>
              </Button>
              <span className="text-muted-foreground">/</span>
              <span className="font-medium">{project.name}</span>
            </div>

            {/* Assistant Toggle */}
            <Sheet>
              <SheetTrigger asChild>
                <Button variant="outline" size="sm" className="gap-2">
                  <Bot className="h-4 w-4" />
                  Assistent
                </Button>
              </SheetTrigger>
              <SheetContent side="right" className="w-[400px] sm:w-[540px] p-0">
                <ChatContextPanel />
              </SheetContent>
            </Sheet>
          </div>
        </div>
      </div>

      {/* Two-Panel Layout: Fixed Sidebar + Content */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left Sidebar — fixed width */}
        <div className="w-64 shrink-0 border-r">
          <ProjectNavigation
            project={project}
            activeSection={activeSection}
            onSectionChange={setActiveSection}
          />
        </div>

        {/* Center Content — fills remaining space */}
        <div className="flex-1 overflow-auto p-6">
          {activeSection === 'overview' && <ProjectOverview project={project} />}
          {activeSection !== 'overview' && (
            <div className="flex items-center justify-center h-full">
              <div className="text-center space-y-2">
                <p className="text-muted-foreground">
                  {activeSection.charAt(0).toUpperCase() + activeSection.slice(1)} sectie
                  binnenkort beschikbaar
                </p>
                <p className="text-sm text-muted-foreground/70">Deze functie wordt in een volgende fase gebouwd</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
