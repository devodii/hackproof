import { Link } from '@/components/hackathon/hackathon-link'

import { BackButton } from '@/components/back-button'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { useWrapped } from '@/hooks/use-wrapped'
import { useHackathon } from '@/hooks/use-hackathon'
import { formatNumber, projectName } from '@/lib/format'

export function ContributorsPage() {
  const { data, isPending, isError } = useWrapped()
  const hackathon = useHackathon()

  if (isError) {
    return (
      <Alert variant="destructive">
        <AlertTitle>Could not load builders</AlertTitle>
        <AlertDescription>The API is unreachable. Try again in a moment.</AlertDescription>
      </Alert>
    )
  }

  const builders = data?.multi_team_builders ?? []

  return (
    <div className="flex flex-col gap-8">
      <header className="flex flex-col items-start gap-3">
        <BackButton />
        <h1 className="font-heading text-4xl leading-tight text-balance sm:text-6xl">
          <span className="text-muted-foreground">{hackathon.name} builders</span> on 2 or more
          teams
        </h1>
        <p className="text-muted-foreground">
          {isPending
            ? 'Counting…'
            : `${builders.length} builders committed to more than one project, by commits to the default branch.`}
        </p>
      </header>
      <ul className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        {isPending
          ? Array.from({ length: 6 }, (_, index) => (
              <li key={index}>
                <Skeleton className="h-32" />
              </li>
            ))
          : builders.map((builder) => (
              <li key={builder.login}>
                <Link
                  to={`/builder/${encodeURIComponent(builder.login)}`}
                  className="flex h-full flex-col gap-3 rounded-xl border bg-card p-4 transition-colors hover:bg-muted/40"
                >
                  <div className="flex items-center gap-3">
                    <Avatar size="lg">
                      {builder.avatar_url && <AvatarImage src={builder.avatar_url} alt="" />}
                      <AvatarFallback>{builder.login.slice(0, 2).toUpperCase()}</AvatarFallback>
                    </Avatar>
                    <div className="flex min-w-0 flex-col">
                      <span translate="no" className="truncate font-medium">
                        {builder.login}
                      </span>
                      <span className="text-sm text-muted-foreground">
                        {builder.projects} projects · {formatNumber(builder.contributions)} commits
                      </span>
                    </div>
                  </div>
                  <div className="flex flex-wrap gap-1">
                    {builder.project_names.map((name) => (
                      <Badge key={name} variant="secondary" translate="no">
                        {projectName(`repo:${name}`)}
                      </Badge>
                    ))}
                  </div>
                </Link>
              </li>
            ))}
      </ul>
    </div>
  )
}
