import { ClaimProof } from '@/components/claim-proof'
import { Explorer } from '@/components/explorer/explorer'
import { StatsGrid } from '@/components/stats-grid'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { useHackWindow } from '@/hooks/use-hack-window'
import { formatDateTime } from '@/lib/format'

export function HomePage() {
  const { data } = useHackWindow()

  return (
    <div className="flex flex-col gap-10">
      <section className="flex flex-col items-start gap-5">
        <Badge variant="secondary">testnet, rebuilt from the chain</Badge>
        <h1 className="max-w-3xl text-4xl font-semibold tracking-tight sm:text-5xl">
          Every submission to HackMeridian, recovered from the ledger.
        </h1>
        <p className="max-w-2xl text-muted-foreground">
          No public list exists, so we rebuilt it from testnet: every contract deployed, every wasm
          upload and every failed transaction inside the 27 hour window.
        </p>
        {data ? (
          <p className="font-mono text-sm text-muted-foreground">
            {formatDateTime(data.start)} to {formatDateTime(data.end)}
          </p>
        ) : (
          <Skeleton className="h-5 w-72" />
        )}
      </section>
      <StatsGrid />
      <ClaimProof />
      <Explorer />
    </div>
  )
}
