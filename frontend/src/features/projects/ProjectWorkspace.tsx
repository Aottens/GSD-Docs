import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Panel, Group, Separator } from 'react-resizable-panels'
import { GripVertical, ArrowLeft } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { ErrorMessage } from '@/components/common/ErrorMessage'
import { ProjectNavigation } from './components/ProjectNavigation'
import { ProjectOverview } from './components/ProjectOverview'
import { ChatContextPanel } from './components/ChatContextPanel'
import { useProject } from './queries'
import { cn } from '@/lib/utils'

const PANEL_STORAGE_KEY = 'project-workspace-panels'

export function ProjectWorkspace() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [activeSection, setActiveSection] = useState('overview')

  const { data: project, isLoading, error, refetch } = useProject(id || '')

  // Persist panel sizes to localStorage
  const handleLayoutChange = (layout: { [id: string]: number }) => {
    localStorage.setItem(PANEL_STORAGE_KEY, JSON.stringify(layout))
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background">
        <div className="container py-8">
          <Skeleton className="h-8 w-64 mb-6" />
          <div className="flex gap-4">
            <Skeleton className="h-[600px] w-64" />
            <Skeleton className="h-[600px] flex-1" />
            <Skeleton className="h-[600px] w-80" />
          </div>
        </div>
      </div>
    )
  }

  if (error || !project) {
    return (
      <div className="min-h-screen bg-background">
        <div className="container py-8">
          <Button variant="ghost" onClick={() => navigate('/')} className="mb-6">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Dashboard
          </Button>
          <ErrorMessage
            title="Project not found"
            message={
              error instanceof Error ? error.message : 'The requested project could not be found.'
            }
            onRetry={() => refetch()}
          />
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Breadcrumb Header */}
      <div className="border-b bg-background">
        <div className="container py-4">
          <div className="flex items-center gap-2 text-sm">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => navigate('/')}
              className="h-auto p-0 hover:bg-transparent"
            >
              <span className="text-muted-foreground hover:text-foreground">Projects</span>
            </Button>
            <span className="text-muted-foreground">/</span>
            <span className="font-medium">{project.name}</span>
          </div>
        </div>
      </div>

      {/* Three-Panel Layout */}
      <div className="flex-1 overflow-hidden">
        <Group
          orientation="horizontal"
          onLayoutChange={handleLayoutChange}
          className="h-full"
        >
          {/* Left Sidebar */}
          <Panel
            id="sidebar"
            defaultSize={20}
            minSize={15}
            maxSize={30}
            className="border-r"
          >
            <ProjectNavigation
              project={project}
              activeSection={activeSection}
              onSectionChange={setActiveSection}
            />
          </Panel>

          <Separator className={cn(
            "bg-border relative flex w-px items-center justify-center",
            "after:absolute after:inset-y-0 after:left-1/2 after:w-1 after:-translate-x-1/2",
            "focus-visible:ring-1 focus-visible:ring-ring focus-visible:ring-offset-1 focus-visible:outline-hidden"
          )}>
            <div className="bg-border z-10 flex h-4 w-3 items-center justify-center rounded-xs border">
              <GripVertical className="h-2.5 w-2.5" />
            </div>
          </Separator>

          {/* Center Content */}
          <Panel id="content" defaultSize={55} minSize={40}>
            <div className="h-full overflow-auto p-6">
              {activeSection === 'overview' && <ProjectOverview project={project} />}
              {activeSection !== 'overview' && (
                <div className="flex items-center justify-center h-full">
                  <div className="text-center space-y-2">
                    <p className="text-muted-foreground">
                      {activeSection.charAt(0).toUpperCase() + activeSection.slice(1)} section
                      coming soon
                    </p>
                    <p className="text-sm text-muted-foreground/70">This feature is planned for future phases</p>
                  </div>
                </div>
              )}
            </div>
          </Panel>

          <Separator className={cn(
            "bg-border relative flex w-px items-center justify-center",
            "after:absolute after:inset-y-0 after:left-1/2 after:w-1 after:-translate-x-1/2",
            "focus-visible:ring-1 focus-visible:ring-ring focus-visible:ring-offset-1 focus-visible:outline-hidden"
          )}>
            <div className="bg-border z-10 flex h-4 w-3 items-center justify-center rounded-xs border">
              <GripVertical className="h-2.5 w-2.5" />
            </div>
          </Separator>

          {/* Right Panel (Chat/Context) */}
          <Panel
            id="assistant"
            defaultSize={25}
            minSize={20}
            maxSize={35}
            className="border-l"
          >
            <ChatContextPanel />
          </Panel>
        </Group>
      </div>
    </div>
  )
}
