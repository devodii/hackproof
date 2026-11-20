import * as React from 'react'
import { useSearchParams } from 'react-router'

import { HackathonCard } from '@/components/hackathon/hackathon-card'
import { HackathonFilterBar } from '@/components/hackathon/hackathon-filters'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Skeleton } from '@/components/ui/skeleton'
import { useHackathons } from '@/hooks/use-hackathons'
import { formatNumber } from '@/lib/format'
import {
  filterHackathons,
  readFilters,
  writeFilters,
  yearsOf,
  type HackathonFilters,
} from '@/lib/hackathons'

function CardsSkeleton() {
  return (
    <div className="grid gap-4 md:grid-cols-2">
      {Array.from({ length: 4 }, (_, index) => (
        <Skeleton key={index} className="h-48 rounded-xl" />
      ))}
    </div>
  )
}

export function HackathonsPage() {
  const { data, isPending, isError } = useHackathons()
  const [params, setParams] = useSearchParams()
  const filters = readFilters(params)
  const update = React.useCallback(
    (next: HackathonFilters) => setParams(writeFilters(next), { replace: true }),
    [setParams],
  )
  const shown = data ? filterHackathons(data, filters) : []
  const projects = data?.reduce((sum, item) => sum + item.projects, 0) ?? 0

  return (
    <div className="flex flex-col gap-10">
      <section className="flex max-w-3xl flex-col items-start gap-4">
        <h1 className="text-5xl leading-[1.02] text-balance sm:text-7xl">
          Stellar hackathons, checked against the chain.
        </h1>
        <p className="text-lg text-muted-foreground">
          Every project is matched to the on-chain activity behind it, so you can see what was
          really built.
          {data &&
            ` ${formatNumber(projects)} projects across ${formatNumber(data.length)} hackathons.`}
        </p>
      </section>
      {isError ? (
        <Alert variant="destructive">
          <AlertTitle>Could not load the hackathons</AlertTitle>
          <AlertDescription>The API is unreachable. Try again in a moment.</AlertDescription>
        </Alert>
      ) : (
        <>
          <HackathonFilterBar filters={filters} years={yearsOf(data ?? [])} onChange={update} />
          {isPending ? (
            <CardsSkeleton />
          ) : shown.length > 0 ? (
            <div className="grid gap-4 md:grid-cols-2">
              {shown.map((hackathon) => (
                <HackathonCard key={hackathon.slug} hackathon={hackathon} />
              ))}
            </div>
          ) : (
            <Alert>
              <AlertTitle>No hackathon matches</AlertTitle>
              <AlertDescription>Try another search or clear the filters.</AlertDescription>
            </Alert>
          )}
        </>
      )}
    </div>
  )
}
