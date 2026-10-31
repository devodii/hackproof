import { Bar, BarChart, CartesianGrid, ReferenceLine, XAxis, YAxis } from 'recharts'

import {
  type ChartConfig,
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from '@/components/ui/chart'
import type { DeployBucket } from '@/lib/types'

const config = {
  count: { label: 'Projects', color: 'var(--chart-1)' },
} satisfies ChartConfig

interface HistogramProps {
  buckets: DeployBucket[]
  median?: number | null
  className?: string
}

export function Histogram({ buckets, median, className = 'h-52 w-full' }: HistogramProps) {
  const medianBucket =
    median !== null && median !== undefined
      ? buckets.find((b) => median >= b.min_minutes && median < b.max_minutes)?.label
      : undefined

  return (
    <ChartContainer config={config} className={className}>
      <BarChart data={buckets} margin={{ top: 24, right: 16, left: 0, bottom: 5 }}>
        <CartesianGrid vertical={false} strokeWidth={1} />
        <XAxis
          dataKey="label"
          tickLine={false}
          axisLine={false}
          interval="preserveStartEnd"
          tick={{ fontSize: 11 }}
        />
        <YAxis tickLine={false} axisLine={false} width={36} allowDecimals={false} />
        <ChartTooltip
          cursor={{ fill: 'var(--muted)', opacity: 0.3 }}
          content={<ChartTooltipContent labelFormatter={(val) => `Time to deploy: ${val}`} />}
        />
        <Bar dataKey="count" fill="var(--chart-1)" radius={[4, 4, 0, 0]} animationDuration={1000} />
        {medianBucket && (
          <ReferenceLine
            x={medianBucket}
            stroke="var(--chart-2)"
            strokeDasharray="3 3"
            strokeWidth={2}
            label={{
              value: `Median ${median}m`,
              position: 'top',
              fill: 'var(--foreground)',
              fontSize: 11,
            }}
          />
        )}
      </BarChart>
    </ChartContainer>
  )
}
