import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { useHackWindow } from '@/hooks/use-hack-window'

const formatter = new Intl.DateTimeFormat('en', {
  dateStyle: 'medium',
  timeStyle: 'short',
  timeZone: 'UTC',
})

export function HomePage() {
  const { data, isPending } = useHackWindow()

  return (
    <section className="flex flex-col items-start gap-6">
      <Badge variant="secondary">testnet, rebuilt from the chain</Badge>
      <h1 className="max-w-3xl text-4xl font-semibold tracking-tight sm:text-5xl">
        Every submission to HackMeridian, recovered from the ledger.
      </h1>
      <p className="max-w-2xl text-muted-foreground">
        No public list exists, so we rebuilt it from testnet: every contract deployed, every wasm
        upload and every failed transaction inside the 27 hour window.
      </p>
      {isPending || !data ? (
        <Skeleton className="h-5 w-72" />
      ) : (
        <p className="font-mono text-sm text-muted-foreground">
          {formatter.format(new Date(data.start))} to {formatter.format(new Date(data.end))} UTC
        </p>
      )}
    </section>
  )
}
