import { ChartCard } from '@/components/charts/chart-card'
import { TimelineArea } from '@/components/charts/timeline-area'
import { Skeleton } from '@/components/ui/skeleton'
import { useTimeline } from '@/hooks/use-timeline'
import { formatDateTime } from '@/lib/format'

export function ActivityChart() {
  const { data } = useTimeline()

  const peak = data?.reduce((best, point) => (point.contracts > best.contracts ? point : best))

  return (
    <ChartCard
      title="Contracts deployed per hour"
      description="Every Soroban contract deployed on testnet during the 27 hour window, in UTC."
      headers={['Hour (UTC)', 'Contracts']}
      rows={(data ?? []).map((point) => [formatDateTime(point.hour), point.contracts])}
    >
      {data && peak ? (
        <TimelineArea data={data} peak={peak} className="h-[26rem] w-full" />
      ) : (
        <Skeleton className="h-64 w-full" />
      )}
    </ChartCard>
  )
}
