import { ExternalLinkIcon } from 'lucide-react'
import { useParams } from 'react-router'

import { BackButton } from '@/components/back-button'
import { ProjectCard } from '@/components/explorer/project-card'
import { DetailError } from '@/components/query-state'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { usePerson } from '@/hooks/use-person'
import { useHackathon } from '@/hooks/use-hackathon'
import { countryName, flagEmoji, formatNumber } from '@/lib/format'

function PersonSkeleton() {
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

export function PersonPage() {
  const login = useParams().login ?? ''
  const hackathon = useHackathon()
  const { data, isPending, error } = usePerson(login)

  if (isPending) return <PersonSkeleton />
  if (error) return <DetailError error={error} subject="builder" />

  const teams = data.projects.length

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
            <p className="text-sm tracking-wide text-muted-foreground uppercase">
              {hackathon.name} builder
            </p>
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
            {teams} {teams === 1 ? 'project' : 'projects'} at {hackathon.name}
          </span>
          {teams > 1 && <Badge variant="secondary">On {teams} teams</Badge>}
        </p>
      </header>
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        {data.projects.map((item) => (
          <ProjectCard
            key={item.project.project_id}
            project={item.project}
            commits={item.contributions}
          />
        ))}
      </div>
    </div>
  )
}
