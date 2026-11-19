import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import type { ContractState, Reading } from '@/lib/types'

function amount(value: string) {
  const number = Number(value)
  const digits = number >= 100 ? 2 : number >= 1 ? 4 : 6
  return number.toLocaleString('en-US', { maximumFractionDigits: digits })
}

function age(seconds: number) {
  return seconds < 90 ? `${seconds}s ago` : `${Math.round(seconds / 60)}m ago`
}

interface LiveReadingsProps {
  readings: Reading[] | undefined
  contracts: ContractState[]
}

export function LiveReadings({ readings, contracts }: LiveReadingsProps) {
  if (!readings) {
    return (
      <div className="grid grid-cols-2 gap-3 md:grid-cols-3">
        {Array.from({ length: 6 }, (_, index) => (
          <Skeleton key={index} className="h-24 rounded-xl" />
        ))}
      </div>
    )
  }

  return (
    <div className="grid grid-cols-2 gap-3 md:grid-cols-3">
      {readings.map((reading) => {
        const contract = contracts.find((item) => item.slug === reading.contract)

        return (
          <Card key={`${reading.contract}:${reading.subject}`} size="sm">
            <CardContent className="flex flex-col gap-1.5">
              <div className="flex items-center justify-between gap-2">
                <span className="font-mono text-sm font-semibold">{reading.subject}</span>
                {reading.value === null ? (
                  <Badge variant="destructive">No quote</Badge>
                ) : (
                  reading.stale !== null && (
                    <Badge variant={reading.stale ? 'destructive' : 'outline'}>
                      {reading.stale ? 'Stale' : 'Fresh'}
                    </Badge>
                  )
                )}
              </div>
              <span className="font-heading text-3xl leading-none">
                {reading.value === null ? '-' : amount(reading.value)}
              </span>
              <span className="text-xs text-muted-foreground">
                {contract?.name} · {contract?.network}
                {reading.age_seconds !== null && ` · ${age(reading.age_seconds)}`}
                {reading.value === null &&
                  contract?.expired.includes(reading.subject) &&
                  ' · expired'}
              </span>
            </CardContent>
          </Card>
        )
      })}
    </div>
  )
}
