import { ExternalLinkIcon, StarIcon } from 'lucide-react'
import { useParams } from 'react-router'

import { ClientTable } from '@/components/client-table'
import { Contributors } from '@/components/contributors'
import { ActivityTabs } from '@/components/explorer/activity-tabs'
import { linkColumns } from '@/components/explorer/columns'
import { DetailError, DetailSkeleton } from '@/components/query-state'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Badge } from '@/components/ui/badge'
import { useHackWindow } from '@/hooks/use-hack-window'
import { useProject } from '@/hooks/use-project'
import {
  flagEmoji,
  footprintLabel,
  formatDateTime,
  isWithin,
  projectName,
  tierLabel,
} from '@/lib/format'
import { githubUrl } from '@/lib/links'

export function ProjectPage() {
  const projectId = useParams()['*'] ?? ''
  const { data, isPending, error } = useProject(projectId)
  const { data: hackWindow } = useHackWindow()

  if (isPending) return <DetailSkeleton />
  if (error) return <DetailError error={error} subject="project" />

  const { project, links, contributors, contracts, wasm_uploads, failed_txs } = data
  const name = projectName(project.project_id)
  const direct = links.filter((link) => link.method !== 'footprint')
  const derived = links.length - direct.length
  const packages = Object.entries(project.dependencies?.packages ?? {})
  const signals = [
    isWithin(project.created_at, hackWindow) && 'Created during the hack',
    project.stellar_added_in_window && 'Added Stellar during the hack',
    project.mentions_hackathon && 'Mentions HackMeridian',
  ].filter(Boolean)

  return (
    <div className="flex flex-col gap-8">
      <header className="flex flex-col gap-3">
        <div className="flex items-center gap-3">
          <Avatar>
            {project.owner_avatar && (
              <AvatarImage src={project.owner_avatar} alt={project.owner ?? ''} />
            )}
            <AvatarFallback>{name.slice(0, 2).toUpperCase()}</AvatarFallback>
          </Avatar>
          <h1 className="text-3xl font-semibold tracking-tight">{name}</h1>
          {project.country && <span title={project.country}>{flagEmoji(project.country)}</span>}
          <Badge variant={project.tier === 'verified' ? 'default' : 'secondary'}>
            {tierLabel[project.tier]}
          </Badge>
          <Badge variant="outline">{footprintLabel[project.footprint]}</Badge>
        </div>
        {project.description && (
          <p className="max-w-2xl text-muted-foreground">{project.description}</p>
        )}
        <div className="flex flex-wrap items-center gap-x-4 gap-y-2 text-sm text-muted-foreground">
          {project.url ? (
            <a
              href={project.url}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-1 hover:text-foreground"
            >
              GitHub <ExternalLinkIcon className="size-3.5" />
            </a>
          ) : (
            <Badge variant="outline">no repo linked</Badge>
          )}
          {project.owner && (
            <a
              href={githubUrl.profile(project.owner)}
              target="_blank"
              rel="noreferrer"
              className="hover:text-foreground"
            >
              by {project.owner}
            </a>
          )}
          {project.homepage && (
            <a
              href={project.homepage}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-1 hover:text-foreground"
            >
              Demo <ExternalLinkIcon className="size-3.5" />
            </a>
          )}
          {project.language && <span>{project.language}</span>}
          {project.license && <span>{project.license}</span>}
          {project.forks !== null && project.forks > 0 && <span>{project.forks} forks</span>}
          {project.stars !== null && (
            <span className="inline-flex items-center gap-1">
              <StarIcon className="size-3.5" /> {project.stars}
            </span>
          )}
          {project.first_activity && project.last_activity && (
            <span>
              {formatDateTime(project.first_activity)} to {formatDateTime(project.last_activity)}
            </span>
          )}
          {project.full_name &&
            hackWindow &&
            project.window_commits !== null &&
            project.total_commits !== null && (
              <a
                href={githubUrl.commits(project.full_name, hackWindow)}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-1 hover:text-foreground"
              >
                {project.window_commits} of {project.total_commits} commits inside the window
                <ExternalLinkIcon className="size-3.5" />
              </a>
            )}
        </div>
        {signals.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {signals.map((signal) => (
              <Badge key={String(signal)}>{signal}</Badge>
            ))}
          </div>
        )}
        {packages.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {packages.map(([pkg, version]) => (
              <Badge key={pkg} variant="outline" className="font-mono">
                {pkg}
                {version && ` ${version}`}
              </Badge>
            ))}
          </div>
        )}
      </header>
      {contributors.length > 0 && (
        <section className="flex flex-col gap-3">
          <h2 className="text-lg font-medium">Contributors ({contributors.length})</h2>
          <Contributors contributors={contributors} />
        </section>
      )}
      {direct.length > 0 && (
        <section className="flex flex-col gap-3">
          <h2 className="text-lg font-medium">Why this is linked</h2>
          <p className="max-w-2xl text-sm text-muted-foreground">
            Each match below is an exact string found in the repo and on testnet. Open the file to
            see it in the code, and the explorer link to see it on chain.
            {derived > 0 &&
              ` ${derived} more contracts, accounts and assets are attributed through the same deploy accounts and are listed in the tables below.`}
          </p>
          <ClientTable
            columns={linkColumns(project.full_name ?? '')}
            rows={direct}
            rowKey={(row) => `${row.subject_kind}:${row.subject}`}
            empty="No links."
          />
        </section>
      )}
      <ActivityTabs contracts={contracts} wasmUploads={wasm_uploads} failedTxs={failed_txs} />
    </div>
  )
}
