import { useState } from 'react'
import { Area, AreaChart, CartesianGrid, ReferenceDot, XAxis, YAxis } from 'recharts'

import {
  type ChartConfig,
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from '@/components/ui/chart'
import { formatDateTime, formatHour, formatNumber } from '@/lib/format'
import type { TimelinePoint } from '@/lib/types'

const config = {
  contracts: { label: 'Contracts deployed', color: 'var(--chart-2)' },
} satisfies ChartConfig

interface TimelineAreaProps {
  data: TimelinePoint[]
  peak: TimelinePoint
  className: string
}

export function TimelineArea({ data, peak, className }: TimelineAreaProps) {
  const [drawn, setDrawn] = useState(false)

  return (
    <ChartContainer config={config} className={className}>
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
          animationDuration={1200}
          animationEasing="ease-out"
          onAnimationEnd={() => setDrawn(true)}
          activeDot={{ r: 4, stroke: 'var(--background)', strokeWidth: 2 }}
        />
        {drawn && (
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
        )}
      </AreaChart>
    </ChartContainer>
  )
}
