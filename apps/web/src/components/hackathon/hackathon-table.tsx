import { ArrowUpRightIcon, CrownIcon } from 'lucide-react'
import { motion, useReducedMotion } from 'motion/react'

import { Link } from 'react-router'

import { DataTable, type Column } from '@/components/data-table'
import { Badge } from '@/components/ui/badge'
import { useHackathonNavigate } from '@/components/hackathon/hackathon-link'
import { formatDateRange, formatNumber } from '@/lib/format'
import { hackathonPath } from '@/lib/hackathon'
import type { HackathonSummary } from '@/lib/types'

const STATUS_LABEL: Record<HackathonSummary['status'], string> = {
  live: 'Live now',
  upcoming: 'Upcoming',
  past: 'Past',
}

function Status({ status }: { status: HackathonSummary['status'] }) {
  return (
    <Badge variant={status === 'live' ? 'default' : 'outline'}>
      {status === 'live' && (
        <span className="relative flex size-2">
          <span className="absolute inline-flex size-full animate-ping rounded-full bg-primary-foreground/60" />
          <span className="relative inline-flex size-2 rounded-full bg-primary-foreground" />
        </span>
      )}
      {STATUS_LABEL[status]}
    </Badge>
  )
}

function Projects({ item }: { item: HackathonSummary }) {
  const reduced = useReducedMotion()
  if (!item.indexed) return <span className="text-muted-foreground">Not indexed yet</span>
  const share = item.projects ? (item.verified_projects / item.projects) * 100 : 0

  return (
    <div className="flex min-w-32 flex-col gap-1.5">
      <span className="font-heading text-2xl leading-none">{formatNumber(item.projects)}</span>
      <div className="flex h-1.5 gap-0.5 overflow-hidden rounded-full bg-track">
        <motion.div
          className="bg-primary"
          initial={reduced ? false : { width: 0 }}
          animate={{ width: `${share}%` }}
          transition={{ duration: 0.9, ease: 'easeOut' }}
        />
        <div className="flex-1 bg-primary/30" />
      </div>
      <span className="text-xs text-muted-foreground">
        {formatNumber(item.verified_projects)} verified on-chain
      </span>
    </div>
  )
}

const columns: Column<HackathonSummary>[] = [
  {
    header: 'Hackathon',
    cell: (item) => (
      <div className="flex flex-col gap-0.5">
        <Link
          to={hackathonPath(item.slug)}
          translate="no"
          className="font-heading text-2xl leading-tight hover:underline"
        >
          {item.name}
        </Link>
        {item.location && <span className="text-xs text-muted-foreground">{item.location}</span>}
      </div>
    ),
  },
  {
    header: 'Dates',
    cell: (item) => (
      <span className="text-muted-foreground">{formatDateRange(item.starts_at, item.ends_at)}</span>
    ),
  },
  { header: 'Status', cell: (item) => <Status status={item.status} /> },
  { header: 'Projects', cell: (item) => <Projects item={item} /> },
  {
    header: 'Contracts',
    className: 'text-right',
    cell: (item) =>
      item.indexed ? (
        <span className="tabular-nums">{formatNumber(item.contracts)}</span>
      ) : (
        <span className="text-muted-foreground">–</span>
      ),
  },
  {
    header: 'Winners',
    className: 'text-right',
    cell: (item) =>
      item.winners > 0 ? (
        <span className="inline-flex items-center gap-1 tabular-nums">
          <CrownIcon className="size-3.5 text-award-first" /> {item.winners}
        </span>
      ) : (
        <span className="text-muted-foreground">–</span>
      ),
  },
  {
    header: '',
    className: 'w-10 text-right',
    cell: () => <ArrowUpRightIcon className="ml-auto size-4 text-muted-foreground" />,
  },
]

export function HackathonTable({
  hackathons,
  isLoading,
}: {
  hackathons: HackathonSummary[]
  isLoading: boolean
}) {
  const navigate = useHackathonNavigate()

  return (
    <DataTable
      columns={columns}
      rows={hackathons}
      rowKey={(item) => item.slug}
      isLoading={isLoading}
      empty="No hackathon matches. Try another search or clear the filters."
      onRowClick={(item) => navigate(hackathonPath(item.slug))}
    />
  )
}
