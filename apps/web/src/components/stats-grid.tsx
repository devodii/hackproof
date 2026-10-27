import { Card, CardContent } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { useStats } from '@/hooks/use-stats'
import { formatNumber } from '@/lib/format'
import type { Stats } from '@/lib/types'

const ITEMS: { key: keyof Stats; label: string }[] = [
  { key: 'projects', label: 'Projects' },
  { key: 'contracts', label: 'Contracts' },
  { key: 'builders', label: 'Builders' },
  { key: 'countries', label: 'Countries' },
  { key: 'wasm_uploads', label: 'Wasm uploads' },
  { key: 'failed_txs', label: 'Failed txs' },
]

export function StatsGrid() {
  const { data } = useStats()

  return (
    <div className="grid w-full grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
      {ITEMS.map(({ key, label }) => (
        <Card key={key} size="sm">
          <CardContent className="flex flex-col gap-1">
            <span className="text-xs text-muted-foreground">{label}</span>
            {data ? (
              <span className="text-2xl font-semibold tabular-nums">{formatNumber(data[key])}</span>
            ) : (
              <Skeleton className="h-8 w-16" />
            )}
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
