import { ExternalLinkIcon, StarIcon } from 'lucide-react'
import { Link } from 'react-router'

import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { flagEmoji, formatNumber, projectName, tierLabel } from '@/lib/format'
import type { Project } from '@/lib/types'

const VISIBLE_TOPICS = 3

export function ProjectCard({ project }: { project: Project }) {
  const name = projectName(project.project_id)
  const topics = (project.topics ?? []).slice(0, VISIBLE_TOPICS)

  return (
    <Card size="sm" className="relative h-full transition-colors hover:bg-muted/40">
      <CardHeader>
        <div className="flex items-start gap-3">
          <Avatar>
            {project.owner_avatar && (
              <AvatarImage src={project.owner_avatar} alt={project.owner ?? ''} />
            )}
            <AvatarFallback>{name.slice(0, 2).toUpperCase()}</AvatarFallback>
          </Avatar>
          <div className="flex min-w-0 flex-1 flex-col items-start gap-1">
            <Link
              to={`/project/${project.project_id}`}
              className="max-w-full truncate font-medium after:absolute after:inset-0"
            >
              {name}
            </Link>
            <Badge variant={project.tier === 'verified' ? 'default' : 'secondary'}>
              {tierLabel[project.tier]}
            </Badge>
          </div>
          {project.country && <span title={project.country}>{flagEmoji(project.country)}</span>}
          {project.url && (
            <a
              href={project.url}
              target="_blank"
              rel="noreferrer"
              aria-label="Open the repo on GitHub"
              className="relative z-10 text-muted-foreground hover:text-foreground"
            >
              <ExternalLinkIcon className="size-4" />
            </a>
          )}
        </div>
      </CardHeader>
      <CardContent className="flex flex-col gap-3">
        <p className="line-clamp-2 min-h-10 text-sm text-muted-foreground">
          {project.description ?? 'No description'}
        </p>
        <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-muted-foreground">
          {project.language && <span>{project.language}</span>}
          {project.stars !== null && project.stars > 0 && (
            <span className="inline-flex items-center gap-1">
              <StarIcon className="size-3" /> {formatNumber(project.stars)}
            </span>
          )}
          {project.contracts > 0 && <span>{formatNumber(project.contracts)} contracts</span>}
        </div>
        {topics.length > 0 && (
          <div className="flex flex-wrap gap-1">
            {topics.map((topic) => (
              <Badge key={topic} variant="outline">
                {topic}
              </Badge>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
