import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { ErrorMessage } from '@/components/common/ErrorMessage'
import { ProjectNavigation } from './components/ProjectNavigation'
import { ProjectOverview } from './components/ProjectOverview'
import { ReferenceManager } from '../files/components/ReferenceManager'
import { PhaseTimeline } from '../timeline/components/PhaseTimeline'
import { FaseringTab } from '../timeline/components/FaseringTab'
import { DocumentsTab } from '../documents/components/DocumentsTab'
import { ExportTab } from '../export/components/ExportTab'
import { SdsTab } from '../sds/components/SdsTab'
import { useProject } from './queries'
import { usePhaseTimeline } from '../timeline/hooks/usePhaseStatus'

export function ProjectWorkspace() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [activeSection, setActiveSection] = useState('overview')

  const { data: project, isLoading, error, refetch } = useProject(id || '')

  const { data: phaseTimelineData } = usePhaseTimeline(project?.id ?? 0)
  // Find the most recent phase that has verification data (for review)
  const activePhaseForReview = phaseTimelineData?.phases
    ?.filter(p => p.has_verification)
    ?.sort((a, b) => b.number - a.number)[0]?.number

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

      {/* Phase Timeline Bar */}
      <PhaseTimeline projectId={project.id} />

      {/* Two-Panel Layout: Fixed Sidebar + Content */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left Sidebar */}
        <div className="w-64 shrink-0 border-r">
          <ProjectNavigation
            project={project}
            activeSection={activeSection}
            onSectionChange={setActiveSection}
          />
        </div>

        {/* Center Content */}
        <div className={`flex-1 ${
          activeSection === 'documents' ? 'overflow-hidden' :
          activeSection === 'export' || activeSection === 'sds' ? 'overflow-auto' :
          'overflow-auto p-6'
        }`}>
          {activeSection === 'overview' && (
            <ProjectOverview project={project} onNavigate={setActiveSection} />
          )}
          {activeSection === 'references' && <ReferenceManager projectId={project.id} />}
          {activeSection === 'fasering' && <FaseringTab projectId={project.id} />}
          {activeSection === 'documents' && (
            <DocumentsTab
              projectId={project.id}
              language={project.language}
              activePhaseNumber={activePhaseForReview}
            />
          )}
          {activeSection === 'export' && (
            <ExportTab projectId={project.id} language={project.language} />
          )}
          {activeSection === 'sds' && (
            <SdsTab projectId={project.id} />
          )}
          {activeSection !== 'overview' &&
            activeSection !== 'references' &&
            activeSection !== 'fasering' &&
            activeSection !== 'documents' &&
            activeSection !== 'export' &&
            activeSection !== 'sds' && (
              <div className="flex items-center justify-center h-full">
                <div className="text-center space-y-2">
                  <p className="text-muted-foreground">
                    {activeSection.charAt(0).toUpperCase() + activeSection.slice(1)} sectie
                    binnenkort beschikbaar
                  </p>
                  <p className="text-sm text-muted-foreground/70">
                    Deze functie wordt in een volgende fase gebouwd
                  </p>
                </div>
              </div>
            )}
        </div>
      </div>
    </div>
  )
}
