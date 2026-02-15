import { useState } from 'react'
import { Plus } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import { ErrorMessage } from '@/components/common/ErrorMessage'
import { RecentProjects } from './components/RecentProjects'
import { DashboardFilters } from './components/DashboardFilters'
import { ProjectGrid } from './components/ProjectGrid'
import { ProjectListSkeleton } from './components/ProjectListSkeleton'
import { useProjects } from './queries'
import type { FilterState } from './types'

export function Dashboard() {
  const navigate = useNavigate()
  const [filters, setFilters] = useState<FilterState>({
    tab: 'all',
    search: '',
    sortBy: 'updated_at',
    sortOrder: 'desc',
  })

  const { data, isLoading, error, refetch } = useProjects({
    status: filters.tab,
    search: filters.search || undefined,
    sortBy: filters.sortBy,
    sortOrder: filters.sortOrder,
  })

  return (
    <div className="min-h-screen bg-background">
      <div className="container py-8 space-y-8">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold tracking-tight">Projects</h1>
            <p className="text-muted-foreground mt-1">
              Manage your FDS/SDS documentation projects
            </p>
          </div>
          <Button onClick={() => navigate('/projects/new')}>
            <Plus className="mr-2 h-4 w-4" />
            New Project
          </Button>
        </div>

        {/* Recent Projects */}
        <RecentProjects />

        <Separator />

        {/* Filters */}
        <DashboardFilters filters={filters} onFiltersChange={setFilters} />

        {/* Project Grid */}
        {isLoading ? (
          <ProjectListSkeleton />
        ) : error ? (
          <ErrorMessage
            title="Failed to load projects"
            message={error instanceof Error ? error.message : 'An unexpected error occurred'}
            onRetry={() => refetch()}
          />
        ) : (
          <ProjectGrid projects={data?.projects || []} />
        )}
      </div>
    </div>
  )
}
