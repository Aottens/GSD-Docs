import { LayoutDashboard, Calendar, FileText, FolderOpen, Settings } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import type { Project } from '@/types/project'

interface ProjectNavigationProps {
  project: Project
  activeSection: string
  onSectionChange: (sectionId: string) => void
}

const navigationSections = [
  { id: 'overview', label: 'Overview', icon: LayoutDashboard },
  { id: 'phases', label: 'Phases', icon: Calendar },
  { id: 'documents', label: 'Documents', icon: FileText },
  { id: 'references', label: 'References', icon: FolderOpen },
  { id: 'settings', label: 'Settings', icon: Settings },
]

const typeColors = {
  A: 'bg-blue-500/10 text-blue-500 border-blue-500/20',
  B: 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20',
  C: 'bg-amber-500/10 text-amber-500 border-amber-500/20',
  D: 'bg-rose-500/10 text-rose-500 border-rose-500/20',
}

export function ProjectNavigation({
  project,
  activeSection,
  onSectionChange,
}: ProjectNavigationProps) {
  return (
    <div className="flex flex-col h-full bg-muted/30">
      {/* Project Header */}
      <div className="p-4 space-y-2">
        <h2 className="font-semibold truncate" title={project.name}>
          {project.name}
        </h2>
        <div className="flex items-center gap-2">
          <Badge variant="outline" className={typeColors[project.type]}>
            Type {project.type}
          </Badge>
          <Badge variant="outline" className="text-xs">
            {project.language.toUpperCase()}
          </Badge>
        </div>
      </div>

      <Separator />

      {/* Navigation Items */}
      <nav className="flex-1 p-2 space-y-1">
        {navigationSections.map((section) => {
          const Icon = section.icon
          const isActive = activeSection === section.id

          return (
            <button
              key={section.id}
              onClick={() => onSectionChange(section.id)}
              className={`
                w-full flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors
                ${
                  isActive
                    ? 'bg-primary text-primary-foreground'
                    : 'hover:bg-muted text-muted-foreground hover:text-foreground'
                }
                ${!isActive && section.id !== 'overview' ? 'opacity-60' : ''}
              `}
              disabled={section.id !== 'overview'}
              title={section.id !== 'overview' ? 'Coming in future phases' : undefined}
            >
              <Icon className="h-4 w-4 flex-shrink-0" />
              <span className="truncate">{section.label}</span>
              {section.id !== 'overview' && !isActive && (
                <span className="ml-auto text-xs opacity-50">Soon</span>
              )}
            </button>
          )
        })}
      </nav>
    </div>
  )
}
