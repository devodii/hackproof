import { useState } from 'react'
import { Area, AreaChart, CartesianGrid, ReferenceArea, ReferenceDot, XAxis, YAxis } from 'recharts'

import { type ChartConfig, ChartContainer } from '@/components/ui/chart'
import { useStill } from '@/components/wrapped/use-still'
import { useMediaQuery } from '@/hooks/use-media-query'
import { formatHour } from '@/lib/format'
import type { TimelinePoint } from '@/lib/types'
import { POSTER_MEDIA } from '@/lib/wrapped'
import { cn } from '@/lib/utils'

const day = new Intl.DateTimeFormat('en', { month: 'short', day: 'numeric', timeZone: 'UTC' })

function tickLabel(iso: string) {
  const hour = formatHour(iso)
  return hour === '00:00' ? day.format(new Date(iso)) : hour
}

const WIDE_TICK_HOURS = 3
const NARROW_TICK_HOURS = 6

const config = {
  contracts: { label: 'Contracts deployed', color: 'var(--primary)' },
} satisfies ChartConfig

interface TimelineChartProps {
  data: TimelinePoint[]
  peak: TimelinePoint
  rush: TimelinePoint[]
  className?: string
}

export function TimelineChart({ data, peak, rush, className }: TimelineChartProps) {
  const still = useStill()
  const wide = useMediaQuery(POSTER_MEDIA)
  const step = wide ? WIDE_TICK_HOURS : NARROW_TICK_HOURS
  const ticks = data.filter((_, index) => index % step === 0).map((point) => point.hour)
  const [drawn, setDrawn] = useState(still)

  return (
    <ChartContainer config={config} className={cn('poster-chart aspect-auto w-full', className)}>
      <AreaChart data={data} margin={{ top: 12, right: 8, left: -12, bottom: 0 }}>
        <defs>
          <linearGradient id="wrapped-fill" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="var(--primary)" stopOpacity={0.55} />
            <stop offset="100%" stopColor="var(--primary)" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid vertical={false} stroke="var(--gridline)" />
        <XAxis
          dataKey="hour"
          tickFormatter={tickLabel}
          ticks={ticks}
          tickLine={false}
          axisLine={false}
        />
        <YAxis tickLine={false} axisLine={false} width={44} />
        {drawn && (
          <ReferenceArea
            x1={rush[0].hour}
            x2={rush[rush.length - 1].hour}
            fill="var(--secondary)"
            fillOpacity={0.18}
            stroke="var(--secondary)"
            strokeOpacity={0.5}
            strokeDasharray="3 3"
          />
        )}
        <Area
          dataKey="contracts"
          type="monotone"
          stroke="var(--primary)"
          strokeWidth={2.5}
          fill="url(#wrapped-fill)"
          dot={false}
          isAnimationActive={!still}
          animationDuration={1800}
          animationEasing="ease-out"
          onAnimationEnd={() => setDrawn(true)}
        />
        {drawn && (
          <ReferenceDot
            x={peak.hour}
            y={peak.contracts}
            r={5}
            fill="var(--primary)"
            stroke="var(--background)"
            strokeWidth={2}
          />
        )}
      </AreaChart>
    </ChartContainer>
  )
}
