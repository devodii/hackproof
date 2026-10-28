import { Area, AreaChart, CartesianGrid, ReferenceDot, XAxis, YAxis } from 'recharts'

import { ChartCard } from '@/components/charts/chart-card'
import { Skeleton } from '@/components/ui/skeleton'
import {
  type ChartConfig,
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from '@/components/ui/chart'
import { useTimeline } from '@/hooks/use-timeline'
import { formatDateTime, formatHour, formatNumber } from '@/lib/format'

const config = {
  contracts: { label: 'Contracts deployed', color: 'var(--chart-2)' },
} satisfies ChartConfig

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
        <ChartContainer config={config} className="h-[26rem] w-full">
          <AreaChart data={data} margin={{ top: 24, right: 16, left: 0 }}>
            <CartesianGrid vertical={false} strokeWidth={1} />
            <XAxis
              dataKey="hour"
              tickFormatter={formatHour}
              interval={5}
              tickLine={false}
              axisLine={false}
            />
            <YAxis tickLine={false} axisLine={false} width={44} />
            <ChartTooltip
              cursor={{ strokeWidth: 1 }}
              content={
                <ChartTooltipContent
                  indicator="line"
                  labelFormatter={(_, items) => formatDateTime(items[0]?.payload.hour)}
                />
              }
            />
            <Area
              dataKey="contracts"
              type="linear"
              stroke="var(--color-contracts)"
              strokeWidth={2}
              fill="var(--color-contracts)"
              fillOpacity={0.1}
              dot={false}
              isAnimationActive={false}
              activeDot={{ r: 4, stroke: 'var(--background)', strokeWidth: 2 }}
            />
            <ReferenceDot
              x={peak.hour}
              y={peak.contracts}
              r={4}
              fill="var(--color-contracts)"
              stroke="var(--background)"
              strokeWidth={2}
              label={{
                value: `Peak ${formatNumber(peak.contracts)}`,
                position: 'top',
                fill: 'var(--foreground)',
                fontSize: 12,
              }}
            />
          </AreaChart>
        </ChartContainer>
      ) : (
        <Skeleton className="h-64 w-full" />
      )}
    </ChartCard>
  )
}
