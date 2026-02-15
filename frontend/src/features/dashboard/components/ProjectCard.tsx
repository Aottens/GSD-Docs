import { useNavigate } from 'react-router-dom'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import type { Project } from '@/types/project'
import { motion } from 'motion/react'

interface ProjectCardProps {
  project: Project
}

const typeColorMap = {
  A: 'bg-blue-500 text-white hover:bg-blue-600',
  B: 'bg-emerald-500 text-white hover:bg-emerald-600',
  C: 'bg-amber-500 text-white hover:bg-amber-600',
  D: 'bg-rose-500 text-white hover:bg-rose-600',
}

export function ProjectCard({ project }: ProjectCardProps) {
  const navigate = useNavigate()

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    })
  }

  return (
    <motion.div
      whileHover={{ y: -4 }}
      transition={{ type: 'spring', stiffness: 300, damping: 20 }}
    >
      <Card
        className="cursor-pointer transition-shadow hover:shadow-lg"
        onClick={() => navigate(`/projects/${project.id}`)}
      >
        <CardHeader className="pb-3">
          <div className="flex items-start justify-between gap-2">
            <h3 className="font-bold text-xl line-clamp-2">{project.name}</h3>
            <Badge className={typeColorMap[project.type]} variant="default">
              {project.type}
            </Badge>
          </div>
          <div className="flex items-center gap-2 mt-2">
            <Badge variant="outline">{project.language.toUpperCase()}</Badge>
            <span className="text-sm text-muted-foreground">
              Phase {project.current_phase}
            </span>
          </div>
        </CardHeader>
        <CardContent className="pb-4">
          <div className="space-y-3">
            <div>
              <div className="flex items-center justify-between text-sm mb-1.5">
                <span className="text-muted-foreground">Progress</span>
                <span className="font-medium">{project.progress}%</span>
              </div>
              <Progress value={project.progress} />
            </div>
            <div className="flex items-center justify-between text-sm text-muted-foreground pt-1">
              <span>Modified</span>
              <span>{formatDate(project.updated_at)}</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  )
}
