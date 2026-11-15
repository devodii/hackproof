import { Bar, BarChart, Cell, LabelList, XAxis, YAxis } from 'recharts'

import { type ChartConfig, ChartContainer } from '@/components/ui/chart'
import { useStill } from '@/components/wrapped/use-still'
import { formatNumber } from '@/lib/format'
import type { Count } from '@/lib/types'
import { cn } from '@/lib/utils'

const config = { value: { label: 'Count', color: 'var(--primary)' } } satisfies ChartConfig

const LABEL_WIDTH = 112

export function RankedBars({ data, className }: { data: Count[]; className?: string }) {
  const still = useStill()

  return (
    <ChartContainer config={config} className={cn('poster-chart aspect-auto w-full', className)}>
      <BarChart
        data={data}
        layout="vertical"
        margin={{ top: 0, right: 48, left: 0, bottom: 0 }}
        barCategoryGap="22%"
      >
        <XAxis type="number" hide domain={[0, 'dataMax']} />
        <YAxis
          type="category"
          dataKey="label"
          width={LABEL_WIDTH}
          tickLine={false}
          axisLine={false}
        />
        <Bar
          dataKey="value"
          radius={6}
          background={{ fill: 'var(--track)', radius: 6 }}
          isAnimationActive={!still}
          animationDuration={1300}
          animationEasing="ease-out"
        >
          {data.map((row, index) => (
            <Cell key={row.label} fill={index === 0 ? 'var(--primary)' : 'var(--chart-3)'} />
          ))}
          <LabelList
            dataKey="value"
            position="right"
            formatter={(value) => formatNumber(Number(value))}
          />
        </Bar>
      </BarChart>
    </ChartContainer>
  )
}
