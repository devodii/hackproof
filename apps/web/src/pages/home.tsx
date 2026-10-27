import { Explorer } from '@/components/explorer/explorer'
import { StatsGrid } from '@/components/stats-grid'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { useHackWindow } from '@/hooks/use-hack-window'
import { useStats } from '@/hooks/use-stats'
import { formatDateTime, formatNumber } from '@/lib/format'

export function HomePage() {
  const { data } = useHackWindow()
  const { data: stats } = useStats()

  return (
    <div className="flex flex-col gap-10">
      <section className="flex flex-col items-start gap-5">
        <Badge variant="secondary">testnet, rebuilt from the chain</Badge>
        <h1 className="max-w-4xl text-5xl leading-[1.02] sm:text-7xl">
          Every submission to HackMeridian, recovered from the ledger.
        </h1>
        <p className="max-w-2xl text-muted-foreground">
          No public list exists, so we rebuilt it from testnet: every contract deployed, every wasm
          upload and every failed transaction inside the 27 hour window.
        </p>
        {data ? (
          <p className="text-sm text-muted-foreground">
            {formatDateTime(data.start)} to {formatDateTime(data.end)}
          </p>
        ) : (
          <Skeleton className="h-5 w-72" />
        )}
      </section>
      <div className="flex flex-col gap-3">
        <StatsGrid />
        {stats && (
          <p className="text-sm text-muted-foreground">
            {formatNumber(stats.projects)} HackMeridian projects:{' '}
            {formatNumber(stats.verified_projects)} verified on-chain,{' '}
            {formatNumber(stats.declared_projects)} declared and{' '}
            {formatNumber(stats.likely_projects)} likely. {formatNumber(stats.possible_projects)}{' '}
            weaker candidates and {formatNumber(stats.unattributed_accounts)} deploy accounts with
            no repo are hidden by default. The official submission list is not public.
          </p>
        )}
      </div>
      <Explorer />
    </div>
  )
}
