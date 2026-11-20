import { ArrowRightIcon } from 'lucide-react'
import { motion, useReducedMotion } from 'motion/react'
import * as React from 'react'
import { Link, useSearchParams } from 'react-router'

import { HackathonFilterBar } from '@/components/hackathon/hackathon-filters'
import { HackathonTable } from '@/components/hackathon/hackathon-table'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { Figure } from '@/components/wrapped/figure'
import { Tile } from '@/components/wrapped/tile'
import { useHackathons } from '@/hooks/use-hackathons'
import { hackathonPath } from '@/lib/hackathon'
import {
  filterHackathons,
  readFilters,
  writeFilters,
  yearsOf,
  type HackathonFilters,
} from '@/lib/hackathons'
import { EASE_OUT } from '@/lib/wrapped'

export function HackathonsPage() {
  const reduced = useReducedMotion()
  const { data, isPending, isError } = useHackathons()
  const [params, setParams] = useSearchParams()
  const filters = readFilters(params)
  const update = React.useCallback(
    (next: HackathonFilters) => setParams(writeFilters(next), { replace: true }),
    [setParams],
  )
  const shown = data ? filterHackathons(data, filters) : []
  const indexed = (data ?? []).filter((item) => item.indexed)
  const featured = [...indexed].sort((a, b) => b.starts_at.localeCompare(a.starts_at))[0]
  const totals = [
    ['hackathons', data?.length ?? 0],
    ['projects checked', indexed.reduce((sum, item) => sum + item.projects, 0)],
    ['verified on-chain', indexed.reduce((sum, item) => sum + item.verified_projects, 0)],
    ['contracts linked', indexed.reduce((sum, item) => sum + item.contracts, 0)],
  ] as const

  return (
    <div className="flex flex-col gap-10">
      <motion.section
        initial={reduced ? false : { opacity: 0, y: 18 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.7, ease: EASE_OUT }}
        className="flex max-w-4xl flex-col items-start gap-6"
      >
        <h1 className="font-heading text-5xl leading-[0.98] text-balance sm:text-8xl">
          Stellar hackathons, <span className="text-brand italic">checked on-chain.</span>
        </h1>
        <p className="max-w-2xl text-lg text-muted-foreground">
          We match every project to the contracts, accounts and commits behind it, so you can see
          what was really built, who built it and what it runs on.
        </p>
        {featured && (
          <div className="flex flex-wrap items-center gap-3">
            <Button size="lg" render={<Link to={hackathonPath(featured.slug)} />}>
              Explore <span translate="no">{featured.name}</span> <ArrowRightIcon />
            </Button>
            <Button
              size="lg"
              variant="outline"
              render={<Link to={hackathonPath(featured.slug, '/wrapped')} />}
            >
              See it wrapped
            </Button>
          </div>
        )}
      </motion.section>
      <div className="grid grid-cols-2 gap-3.5 lg:grid-cols-4">
        {totals.map(([label, value], index) => (
          <Tile key={label} title={label} delay={0.15 + index * 0.08}>
            <Figure
              value={value}
              delay={0.4 + index * 0.08}
              className="font-heading text-figure-lg text-brand"
            />
          </Tile>
        ))}
      </div>
      <Tile
        title="Every hackathon"
        note={data ? `${shown.length} of ${data.length}` : undefined}
        delay={0.5}
        className="gap-5 p-6"
      >
        {isError ? (
          <Alert variant="destructive">
            <AlertTitle>Could not load the hackathons</AlertTitle>
            <AlertDescription>The API is unreachable. Try again in a moment.</AlertDescription>
          </Alert>
        ) : (
          <>
            <HackathonFilterBar filters={filters} years={yearsOf(data ?? [])} onChange={update} />
            <HackathonTable hackathons={shown} isLoading={isPending} />
          </>
        )}
      </Tile>
    </div>
  )
}
