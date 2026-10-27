import { Bar, BarChart, LabelList, XAxis, YAxis } from 'recharts'

import { ChartCard } from '@/components/charts/chart-card'
import { Skeleton } from '@/components/ui/skeleton'
import {
  type ChartConfig,
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from '@/components/ui/chart'
import { useCountries } from '@/hooks/use-countries'
import { countryName, flagEmoji } from '@/lib/format'

const config = {
  contributors: { label: 'Contributors', color: 'var(--chart-1)' },
} satisfies ChartConfig

const ROW_HEIGHT = 32

export function CountryChart() {
  const { data } = useCountries()
  const rows = (data ?? []).map((row) => ({
    ...row,
    label: `${flagEmoji(row.country)} ${countryName(row.country)}`,
  }))

  return (
    <ChartCard
      title="Contributors by country"
      description="Contributors to the strict projects who list a location on GitHub. Most do not, so this is a floor."
      headers={['Country', 'Contributors']}
      rows={rows.map((row) => [countryName(row.country), row.contributors])}
    >
      {data ? (
        <ChartContainer
          config={config}
          className="w-full"
          style={{ height: rows.length * ROW_HEIGHT + 16 }}
        >
          <BarChart
            data={rows}
            layout="vertical"
            margin={{ left: 0, right: 36 }}
            barCategoryGap={8}
          >
            <XAxis type="number" hide />
            <YAxis
              type="category"
              dataKey="label"
              tickLine={false}
              axisLine={false}
              width={150}
              interval={0}
            />
            <ChartTooltip cursor={false} content={<ChartTooltipContent hideLabel />} />
            <Bar
              dataKey="contributors"
              fill="var(--color-contributors)"
              radius={[0, 4, 4, 0]}
              barSize={16}
              isAnimationActive={false}
            >
              <LabelList dataKey="contributors" position="right" className="fill-foreground" />
            </Bar>
          </BarChart>
        </ChartContainer>
      ) : (
        <Skeleton className="h-64 w-full" />
      )}
    </ChartCard>
  )
}
