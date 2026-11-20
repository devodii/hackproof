import { ExternalLinkIcon } from 'lucide-react'
import { Link, useParams } from 'react-router'

import { BackButton } from '@/components/back-button'
import { ProjectCard } from '@/components/explorer/project-card'
import { DetailError } from '@/components/query-state'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { useBuilder } from '@/hooks/use-builder'
import { useHackathons } from '@/hooks/use-hackathons'
import { countryName, flagEmoji, formatDateRange, formatNumber } from '@/lib/format'
import { hackathonPath } from '@/lib/hackathon'

function BuilderSkeleton() {
  return (
    <div className="flex flex-col gap-8">
      <div className="flex items-center gap-4">
        <Skeleton className="size-20 shrink-0 rounded-full" />
        <div className="flex flex-col gap-3">
          <Skeleton className="h-10 w-64" />
          <Skeleton className="h-5 w-48" />
        </div>
      </div>
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        <Skeleton className="h-44" />
        <Skeleton className="h-44" />
      </div>
    </div>
  )
}

export function BuilderPage() {
  const login = useParams().login ?? ''
  const { data, isPending, error } = useBuilder(login)
  const { data: hackathons = [] } = useHackathons()

  if (isPending) return <BuilderSkeleton />
  if (error) return <DetailError error={error} subject="builder" />

  const teams = data.projects.length
  const groups = hackathons
    .map((item) => ({
      hackathon: item,
      projects: data.projects.filter((entry) => entry.project.hackathon === item.slug),
    }))
    .filter((group) => group.projects.length > 0)

  return (
    <div className="flex flex-col gap-8">
      <header className="flex flex-col items-start gap-4">
        <BackButton />
        <div className="flex items-center gap-4">
          <Avatar className="size-20">
            {data.avatar_url && <AvatarImage src={data.avatar_url} alt="" />}
            <AvatarFallback>{data.login.slice(0, 2).toUpperCase()}</AvatarFallback>
          </Avatar>
          <div className="flex flex-col items-start gap-2">
            <p className="text-sm tracking-wide text-muted-foreground uppercase">Builder</p>
            <h1 translate="no" className="text-4xl sm:text-5xl">
              {data.login}
            </h1>
            <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-sm text-muted-foreground">
              {data.country && (
                <span>
                  {flagEmoji(data.country)} {countryName(data.country)}
                </span>
              )}
              <a
                href={data.url}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-1 hover:text-foreground"
              >
                GitHub <ExternalLinkIcon className="size-3.5" />
              </a>
            </div>
          </div>
        </div>
        <p className="flex flex-wrap items-center gap-2 text-lg text-muted-foreground">
          <span>
            {formatNumber(data.contributions)} {data.contributions === 1 ? 'commit' : 'commits'} on{' '}
            {teams} {teams === 1 ? 'project' : 'projects'} across {groups.length}{' '}
            {groups.length === 1 ? 'hackathon' : 'hackathons'}
          </span>
          {teams > 1 && <Badge variant="secondary">On {teams} teams</Badge>}
        </p>
      </header>
      {groups.map(({ hackathon, projects }) => (
        <section key={hackathon.slug} className="flex flex-col gap-4">
          <div className="flex flex-wrap items-baseline justify-between gap-2 border-b pb-2">
            <Link
              to={hackathonPath(hackathon.slug)}
              translate="no"
              className="font-heading text-2xl hover:underline"
            >
              {hackathon.name}
            </Link>
            <span className="text-sm text-muted-foreground">
              {formatDateRange(hackathon.starts_at, hackathon.ends_at)} ·{' '}
              {formatNumber(projects.reduce((sum, item) => sum + item.contributions, 0))} commits
            </span>
          </div>
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
            {projects.map((item) => (
              <ProjectCard
                key={item.project.project_id}
                project={item.project}
                commits={item.contributions}
              />
            ))}
          </div>
        </section>
      ))}
    </div>
  )
}
