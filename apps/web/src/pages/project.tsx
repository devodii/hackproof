import { ExternalLinkIcon, StarIcon } from 'lucide-react'
import { useParams } from 'react-router'

import { ActivityTabs } from '@/components/explorer/activity-tabs'
import { DetailError, DetailSkeleton } from '@/components/query-state'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Badge } from '@/components/ui/badge'
import { useProject } from '@/hooks/use-project'
import { flagEmoji, formatDateTime, projectName } from '@/lib/format'

export function ProjectPage() {
  const projectId = useParams()['*'] ?? ''
  const { data, isPending, error } = useProject(projectId)

  if (isPending) return <DetailSkeleton />
  if (error) return <DetailError error={error} subject="project" />

  const { project, contracts, wasm_uploads, failed_txs } = data
  const name = projectName(project.project_id)

  return (
    <div className="flex flex-col gap-8">
      <header className="flex flex-col gap-3">
        <div className="flex items-center gap-3">
          <Avatar>
            {project.owner_avatar && <AvatarImage src={project.owner_avatar} alt={project.owner ?? ''} />}
            <AvatarFallback>{name.slice(0, 2).toUpperCase()}</AvatarFallback>
          </Avatar>
          <h1 className="text-3xl font-semibold tracking-tight">{name}</h1>
          {project.country && <span title={project.country}>{flagEmoji(project.country)}</span>}
        </div>
        {project.description && <p className="max-w-2xl text-muted-foreground">{project.description}</p>}
        <div className="flex flex-wrap items-center gap-2 text-sm text-muted-foreground">
          {project.full_name ? (
            <a
              href={`https://github.com/${project.full_name}`}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-1 hover:text-foreground"
            >
              GitHub <ExternalLinkIcon className="size-3.5" />
            </a>
          ) : (
            <Badge variant="outline">no repo linked</Badge>
          )}
          {project.stars !== null && (
            <span className="inline-flex items-center gap-1">
              <StarIcon className="size-3.5" /> {project.stars}
            </span>
          )}
          <span>
            {formatDateTime(project.first_deployed_at)} to {formatDateTime(project.last_deployed_at)}
          </span>
        </div>
      </header>
      <ActivityTabs contracts={contracts} wasmUploads={wasm_uploads} failedTxs={failed_txs} />
    </div>
  )
}
