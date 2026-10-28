import { motion } from 'motion/react'

import { CountUp } from '@/components/count-up'
import { TimelineArea } from '@/components/charts/timeline-area'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { useStats } from '@/hooks/use-stats'
import { useTimeline } from '@/hooks/use-timeline'
import { formatNumber } from '@/lib/format'
import type { Stats } from '@/lib/types'

const SECONDARY: { key: keyof Stats; label: string }[] = [
  { key: 'builders', label: 'Deploy accounts' },
  { key: 'contributors', label: 'Contributors' },
  { key: 'countries', label: 'Countries' },
  { key: 'wasm_uploads', label: 'Wasm uploads' },
  { key: 'failed_txs', label: 'Failed txs' },
]

function ProjectsCard({ stats }: { stats?: Stats }) {
  const verified = stats ? (stats.verified_projects / stats.projects) * 100 : 0

  return (
    <Card>
      <CardHeader>
        <CardDescription>Projects</CardDescription>
        {stats ? (
          <CardTitle className="text-6xl leading-none">
            <CountUp value={stats.projects} />
          </CardTitle>
        ) : (
          <Skeleton className="h-14 w-28" />
        )}
      </CardHeader>
      <CardContent className="mt-auto flex flex-col gap-4">
        <div className="flex h-2 gap-0.5 overflow-hidden rounded-full bg-muted">
          <motion.div
            className="bg-primary"
            initial={{ width: 0 }}
            animate={{ width: `${verified}%` }}
            transition={{ duration: 0.9, ease: 'easeOut' }}
          />
          <div className="flex-1 bg-primary/35" />
        </div>
        <dl className="flex flex-col gap-2 text-sm">
          <div className="flex items-center justify-between">
            <dt className="flex items-center gap-2 text-muted-foreground">
              <span className="size-2 rounded-full bg-primary" />
              Verified on-chain
            </dt>
            <dd className="tabular-nums">{stats ? formatNumber(stats.verified_projects) : '–'}</dd>
          </div>
          <div className="flex items-center justify-between">
            <dt className="flex items-center gap-2 text-muted-foreground">
              <span className="size-2 rounded-full bg-primary/35" />
              Likely
            </dt>
            <dd className="tabular-nums">{stats ? formatNumber(stats.likely_projects) : '–'}</dd>
          </div>
        </dl>
      </CardContent>
    </Card>
  )
}

function ActivityCard({ contracts }: { contracts?: number }) {
  const { data } = useTimeline()
  const peak = data?.reduce((best, point) => (point.contracts > best.contracts ? point : best))

  return (
    <Card className="lg:col-span-2">
      <CardHeader>
        <CardDescription>Contracts deployed, per hour over the 27 hour window</CardDescription>
        {contracts === undefined ? (
          <Skeleton className="h-14 w-28" />
        ) : (
          <CardTitle className="text-6xl leading-none">
            <CountUp value={contracts} />
          </CardTitle>
        )}
      </CardHeader>
      <CardContent>
        {data && peak ? (
          <TimelineArea data={data} peak={peak} className="h-52 w-full" />
        ) : (
          <Skeleton className="h-52 w-full" />
        )}
      </CardContent>
    </Card>
  )
}

export function Overview() {
  const { data: stats } = useStats()

  return (
    <motion.div
      className="flex flex-col gap-4"
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45, ease: 'easeOut' }}
    >
      <div className="grid gap-4 lg:grid-cols-3">
        <ActivityCard contracts={stats?.contracts} />
        <ProjectsCard stats={stats} />
      </div>
      <dl className="grid grid-cols-2 gap-x-6 gap-y-4 rounded-xl border bg-card px-5 py-4 sm:grid-cols-3 lg:grid-cols-5">
        {SECONDARY.map(({ key, label }) => (
          <div key={key} className="flex flex-col gap-1">
            <dt className="text-xs text-muted-foreground">{label}</dt>
            <dd className="font-heading text-3xl leading-none">
              {stats ? <CountUp value={stats[key]} /> : <Skeleton className="h-7 w-14" />}
            </dd>
          </div>
        ))}
      </dl>
      <p className="text-sm text-muted-foreground">
        A reconstruction: the official submission list is not public.
      </p>
    </motion.div>
  )
}
