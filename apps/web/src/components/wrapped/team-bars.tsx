import { Bar, BarChart, Cell, LabelList, XAxis } from 'recharts'

import { type ChartConfig, ChartContainer } from '@/components/ui/chart'
import { useStill } from '@/components/wrapped/use-still'
import type { Count } from '@/lib/types'
import { cn } from '@/lib/utils'

const config = { value: { label: 'Projects', color: 'var(--primary)' } } satisfies ChartConfig

export function TeamBars({ data, className }: { data: Count[]; className?: string }) {
  const still = useStill()

  return (
    <ChartContainer config={config} className={cn('poster-chart aspect-auto w-full', className)}>
      <BarChart data={data} margin={{ top: 22, right: 4, left: 4, bottom: 0 }} barCategoryGap="14%">
        <XAxis dataKey="label" tickLine={false} axisLine={false} />
        <Bar
          dataKey="value"
          radius={[7, 7, 2, 2]}
          isAnimationActive={!still}
          animationDuration={1300}
          animationEasing="ease-out"
        >
          {data.map((row, index) => (
            <Cell key={row.label} fill={index === 0 ? 'var(--primary)' : 'var(--secondary)'} />
          ))}
          <LabelList dataKey="value" position="top" />
        </Bar>
      </BarChart>
    </ChartContainer>
  )
}
