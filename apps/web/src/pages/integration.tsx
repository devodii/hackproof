import { useParams } from 'react-router'

import { NotFoundPage } from '@/pages/not-found'

import { AdopterCards } from '@/components/integration/adopter-cards'
import { Block } from '@/components/integration/block'
import { CaptureTable } from '@/components/integration/capture-table'
import { ContractTable } from '@/components/integration/contract-table'
import { Hero } from '@/components/integration/hero'
import { LiveReadings } from '@/components/integration/live-readings'
import { SignalTable } from '@/components/integration/signal-table'
import { SurfaceTable } from '@/components/integration/surface-table'
import { DetailError } from '@/components/query-state'
import { Skeleton } from '@/components/ui/skeleton'
import { useIntegration, useIntegrationLive } from '@/hooks/use-integration'
import { ApiError } from '@/lib/api'
import { humanize } from '@/lib/format'

export function IntegrationPage() {
  const { slug = '' } = useParams()
  const { data, isPending, error } = useIntegration(slug)
  const { data: readings } = useIntegrationLive(slug, (data?.live.length ?? 0) > 0)

  if (isPending) return <Skeleton className="h-96 rounded-3xl" />
  if (error instanceof ApiError && error.status === 404) return <NotFoundPage />
  if (error) return <DetailError error={error} subject="integration" />

  return (
    <div className="flex flex-col gap-14">
      <Hero data={data} />

      {data.surfaces.length > 0 && (
        <Block
          eyebrow="Live"
          title={
            <>
              What <span translate="no"> {data.name} </span> runs today
            </>
          }
          note="Refreshed from the source at most once an hour"
        >
          <SurfaceTable surfaces={data.surfaces} />
        </Block>
      )}

      {data.live.length > 0 && (
        <Block eyebrow="On chain" title="Live from the chain">
          <LiveReadings readings={readings} contracts={data.contracts} />
        </Block>
      )}

      {data.contracts.length > 0 && (
        <Block eyebrow="On chain" title="Contracts">
          <ContractTable contracts={data.contracts} />
        </Block>
      )}

      <Block eyebrow="Adoption" title="Who uses it">
        <AdopterCards adopters={data.adopters} />
      </Block>

      <Block eyebrow="Patterns" title="How it is used">
        <SignalTable signals={data.signals} max={data.adopters.length} />
      </Block>

      {Object.entries(data.captures).map(([name, rows]) => (
        <Block key={name} eyebrow="Demand" title={humanize(name.replaceAll('-', ' '))}>
          <CaptureTable rows={rows} contracts={data.contracts} />
        </Block>
      ))}
    </div>
  )
}
