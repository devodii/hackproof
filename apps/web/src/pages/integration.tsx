import { ExternalLinkIcon } from 'lucide-react'
import { useParams } from 'react-router'

import { AdoptersTable } from '@/components/integration/adopters-table'
import { CaptureDemand } from '@/components/integration/capture-demand'
import { CheckTable } from '@/components/integration/check-table'
import { ContractTable } from '@/components/integration/contract-table'
import { LiveReadings } from '@/components/integration/live-readings'
import { SignalBars } from '@/components/integration/signal-bars'
import { DetailError } from '@/components/query-state'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { useIntegration, useIntegrationLive } from '@/hooks/use-integration'
import { formatNumber, humanize } from '@/lib/format'
import type { ReactNode } from 'react'

function Block({ title, children }: { title: string; children: ReactNode }) {
  return (
    <section className="flex flex-col gap-3">
      <h2 className="text-2xl">{title}</h2>
      {children}
    </section>
  )
}

function Stat({ value, label }: { value: string; label: string }) {
  return (
    <Card size="sm">
      <CardContent className="flex flex-col gap-1">
        <span className="font-heading text-4xl leading-none">{value}</span>
        <span className="text-sm text-muted-foreground">{label}</span>
      </CardContent>
    </Card>
  )
}

export function IntegrationPage() {
  const { slug = '' } = useParams()
  const { data, isPending, error } = useIntegration(slug)
  const { data: readings } = useIntegrationLive(slug, (data?.live.length ?? 0) > 0)

  if (isPending) return <Skeleton className="h-96 rounded-xl" />
  if (error) return <DetailError error={error} subject="integration" />

  const expired = data.contracts.reduce((sum, contract) => sum + contract.expired.length, 0)
  const warnings = data.checks.reduce((sum, check) => sum + check.failing, 0)

  return (
    <div className="flex flex-col gap-10">
      <header className="flex flex-col gap-3">
        <div className="flex flex-wrap items-center gap-3">
          <h1 className="text-4xl leading-none sm:text-6xl">{data.name}</h1>
          <Badge variant="outline">{humanize(data.category)}</Badge>
          <a
            href={data.site}
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground"
          >
            {new URL(data.site).host} <ExternalLinkIcon className="size-3.5" />
          </a>
        </div>
        <p className="max-w-3xl text-lg text-muted-foreground">
          How the {formatNumber(data.of_projects)} projects of this hack use {data.name}, read from
          their source and checked against the live contracts.
        </p>
      </header>

      <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
        <Stat
          value={formatNumber(data.adopters.length)}
          label={`of ${data.of_projects} projects`}
        />
        <Stat value={formatNumber(expired)} label="items expired on its contracts" />
        <Stat value={formatNumber(warnings)} label="open findings" />
        <Stat
          value={
            data.overlap
              ? `${formatNumber(data.overlap.matched)}/${formatNumber(data.overlap.total)}`
              : '-'
          }
          label="hack assets the contracts cover"
        />
      </div>

      {data.live.length > 0 && (
        <Block title="Live from the chain">
          <LiveReadings readings={readings} contracts={data.contracts} />
        </Block>
      )}

      <Block title="Contracts">
        <ContractTable contracts={data.contracts} />
      </Block>

      <Block title="Who uses it">
        <AdoptersTable adopters={data.adopters} />
      </Block>

      <Block title="How it is used">
        <SignalBars signals={data.signals} max={data.adopters.length} />
      </Block>

      {data.checks.length > 0 && (
        <Block title="Integration checklist">
          <CheckTable checks={data.checks} />
        </Block>
      )}

      {Object.entries(data.captures).map(([name, rows]) => (
        <Block key={name} title={humanize(name)}>
          <CaptureDemand rows={rows} contracts={data.contracts} />
        </Block>
      ))}
    </div>
  )
}
