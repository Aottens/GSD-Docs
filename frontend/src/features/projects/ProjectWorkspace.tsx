import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { ErrorMessage } from '@/components/common/ErrorMessage'
import {
  ResizablePanelGroup,
  ResizablePanel,
  ResizableHandle,
} from '@/components/ui/resizable'
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
          <Skeleton className="w-80 h-full" />
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
        </div>
      </div>

      {/* Three-Panel Layout */}
      <ResizablePanelGroup orientation="horizontal" className="flex-1">
        {/* Left Sidebar */}
        <ResizablePanel id="sidebar" defaultSize={20} minSize={15} maxSize={30}>
          <ProjectNavigation
            project={project}
            activeSection={activeSection}
            onSectionChange={setActiveSection}
          />
        </ResizablePanel>

        <ResizableHandle withHandle />

        {/* Center Content */}
        <ResizablePanel id="content" defaultSize={55} minSize={40}>
          <div className="h-full overflow-auto p-6">
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
        </ResizablePanel>

        <ResizableHandle withHandle />

        {/* Right Panel (Chat/Context) */}
        <ResizablePanel id="assistant" defaultSize={25} minSize={20} maxSize={35}>
          <ChatContextPanel />
        </ResizablePanel>
      </ResizablePanelGroup>
    </div>
  )
}
