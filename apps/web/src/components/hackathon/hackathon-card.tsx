import { CalendarIcon, CrownIcon, MapPinIcon } from 'lucide-react'
import { Link } from 'react-router'

import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { formatDateRange, formatNumber } from '@/lib/format'
import { hackathonPath } from '@/lib/hackathon'
import type { HackathonSummary } from '@/lib/types'

const STATUS_LABEL: Record<HackathonSummary['status'], string> = {
  live: 'Live now',
  upcoming: 'Upcoming',
  past: 'Past',
}

function Figure({ label, value }: { label: string; value: number }) {
  return (
    <div className="flex flex-col">
      <span className="font-heading text-3xl leading-none">{formatNumber(value)}</span>
      <span className="text-xs text-muted-foreground">{label}</span>
    </div>
  )
}

export function HackathonCard({ hackathon }: { hackathon: HackathonSummary }) {
  return (
    <Card className="relative h-full transition-colors hover:bg-muted/40">
      <CardHeader className="gap-2">
        <div className="flex items-start justify-between gap-3">
          <Link
            to={hackathonPath(hackathon.slug)}
            translate="no"
            className="font-heading text-3xl leading-tight after:absolute after:inset-0"
          >
            {hackathon.name}
          </Link>
          <Badge variant={hackathon.status === 'live' ? 'default' : 'outline'}>
            {STATUS_LABEL[hackathon.status]}
          </Badge>
        </div>
        <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-sm text-muted-foreground">
          <span className="inline-flex items-center gap-1">
            <CalendarIcon className="size-3.5" />
            {formatDateRange(hackathon.starts_at, hackathon.ends_at)}
          </span>
          {hackathon.location && (
            <span className="inline-flex items-center gap-1">
              <MapPinIcon className="size-3.5" />
              {hackathon.location}
            </span>
          )}
        </div>
      </CardHeader>
      <CardContent className="flex flex-col gap-4">
        {hackathon.summary && (
          <p className="line-clamp-3 text-sm text-muted-foreground">{hackathon.summary}</p>
        )}
        {hackathon.indexed ? (
          <div className="flex flex-wrap items-end gap-x-8 gap-y-3">
            <Figure label="projects" value={hackathon.projects} />
            <Figure label="verified on-chain" value={hackathon.verified_projects} />
            <Figure label="linked contracts" value={hackathon.contracts} />
            {hackathon.winners > 0 && (
              <span className="ml-auto inline-flex items-center gap-1 text-sm text-muted-foreground">
                <CrownIcon className="size-3.5" /> {hackathon.winners} winners
              </span>
            )}
          </div>
        ) : (
          <p className="text-sm text-muted-foreground">Not indexed yet.</p>
        )}
      </CardContent>
    </Card>
  )
}
