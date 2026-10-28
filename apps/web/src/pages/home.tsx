import { Explorer } from '@/components/explorer/explorer'
import { Overview } from '@/components/overview'
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
      <Overview />
      <Explorer />
    </div>
  )
}
