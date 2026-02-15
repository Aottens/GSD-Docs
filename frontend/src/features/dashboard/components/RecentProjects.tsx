import { useNavigate } from 'react-router-dom'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Skeleton } from '@/components/ui/skeleton'
import { useRecentProjects } from '../queries'

const typeColorMap = {
  A: 'bg-blue-500 text-white',
  B: 'bg-emerald-500 text-white',
  C: 'bg-amber-500 text-white',
  D: 'bg-rose-500 text-white',
}

export function RecentProjects() {
  const navigate = useNavigate()
  const { data: recentProjects, isLoading } = useRecentProjects()

  // Don't show section if no recent projects
  if (!isLoading && (!recentProjects || recentProjects.length === 0)) {
    return null
  }

  if (isLoading) {
    return (
      <div className="space-y-3">
        <h2 className="text-xl font-semibold">Recent Projects</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Card key={i}>
              <CardContent className="p-4">
                <Skeleton className="h-5 w-32 mb-2" />
                <div className="flex items-center gap-2 mb-3">
                  <Skeleton className="h-5 w-8" />
                  <Skeleton className="h-4 w-16" />
                </div>
                <Skeleton className="h-2 w-full" />
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      <h2 className="text-xl font-semibold">Recent Projects</h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {recentProjects?.slice(0, 4).map((project) => (
          <Card
            key={project.id}
            className="cursor-pointer transition-shadow hover:shadow-md"
            onClick={() => navigate(`/projects/${project.id}`)}
          >
            <CardContent className="p-4">
              <h3 className="font-semibold text-base line-clamp-1 mb-2">
                {project.name}
              </h3>
              <div className="flex items-center gap-2 mb-3">
                <Badge className={typeColorMap[project.type]} variant="default">
                  {project.type}
                </Badge>
                <span className="text-xs text-muted-foreground">
                  {project.progress}%
                </span>
              </div>
              <Progress value={project.progress} className="h-1.5" />
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
