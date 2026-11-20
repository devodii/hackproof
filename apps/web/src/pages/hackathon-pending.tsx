import { ArrowLeftIcon, CalendarIcon, ExternalLinkIcon, MapPinIcon } from 'lucide-react'
import { Link } from 'react-router'

import { Button } from '@/components/ui/button'
import { useHackathon } from '@/hooks/use-hackathon'
import { formatDateRange } from '@/lib/format'

export function HackathonPendingPage() {
  const hackathon = useHackathon()

  return (
    <div className="flex max-w-3xl flex-col items-start gap-5">
      <Button variant="ghost" size="sm" className="-ml-2.5" render={<Link to="/" />}>
        <ArrowLeftIcon /> All hackathons
      </Button>
      <h1 translate="no" className="text-5xl leading-[1.02] text-balance sm:text-7xl">
        {hackathon.name}
      </h1>
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
      {hackathon.summary && <p className="text-lg text-muted-foreground">{hackathon.summary}</p>}
      <p className="text-muted-foreground">
        HackProof has not indexed this hackathon yet, so there are no projects to show.
      </p>
      {hackathon.website && (
        <Button
          variant="outline"
          render={<a href={hackathon.website} target="_blank" rel="noreferrer" />}
        >
          Event page <ExternalLinkIcon />
        </Button>
      )}
    </div>
  )
}
