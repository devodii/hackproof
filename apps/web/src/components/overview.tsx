import { motion } from 'motion/react'
import { useTranslation } from 'react-i18next'

import { TimelineArea } from '@/components/charts/timeline-area'
import { CountUp } from '@/components/count-up'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { useStats } from '@/hooks/use-stats'
import { useTimeline } from '@/hooks/use-timeline'
import { formatNumber, tierLabel } from '@/lib/format'
import type { Stats } from '@/lib/types'

function ProjectsCard({ stats }: { stats?: Stats }) {
  const { t } = useTranslation()
  const verified = stats ? (stats.verified_projects / stats.projects) * 100 : 0

  return (
    <Card>
      <CardHeader>
        <CardDescription>{t('overview.projects')}</CardDescription>
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
              {t('overview.verifiedOnChain')}
            </dt>
            <dd className="tabular-nums">{stats ? formatNumber(stats.verified_projects) : '–'}</dd>
          </div>
          <div className="flex items-center justify-between">
            <dt className="flex items-center gap-2 text-muted-foreground">
              <span className="size-2 rounded-full bg-primary/35" />
              {t('tiers.likely', { defaultValue: tierLabel.likely })}
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
  const { t } = useTranslation()
  const peak = data?.reduce((best, point) => (point.contracts > best.contracts ? point : best))

  return (
    <Card className="lg:col-span-2">
      <CardHeader>
        <CardDescription>{t('overview.contractsPerHour')}</CardDescription>
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
  const { t } = useTranslation()

  const secondary: { key: keyof Stats; label: string }[] = [
    { key: 'builders', label: t('overview.deployAccounts') },
    { key: 'contributors', label: t('overview.contributors') },
    { key: 'countries', label: t('overview.countries') },
    { key: 'wasm_uploads', label: t('overview.wasmUploads') },
    { key: 'failed_txs', label: t('overview.failedTxs') },
  ]

  return (
    <motion.div
      id="overview"
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
        {secondary.map(({ key, label }) => (
          <div key={key} className="flex flex-col gap-1">
            <dt className="text-xs text-muted-foreground">{label}</dt>
            <dd className="font-heading text-3xl leading-none">
              {stats ? <CountUp value={stats[key]} /> : <Skeleton className="h-7 w-14" />}
            </dd>
          </div>
        ))}
      </dl>
      <p className="text-sm text-muted-foreground">
        {t('home.overviewNote')}
      </p>
    </motion.div>
  )
}
