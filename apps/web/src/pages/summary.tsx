import { DownloadIcon } from 'lucide-react'
import { Link } from 'react-router'

import { ActivityChart } from '@/components/charts/activity-chart'
import { CountryChart } from '@/components/charts/country-chart'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { useStats } from '@/hooks/use-stats'
import { formatNumber } from '@/lib/format'
import { DOWNLOADS, LIMITS, STAT_DEFINITIONS, TIER_DEFINITIONS } from '@/lib/stat-definitions'

export function SummaryPage() {
  const { data: stats } = useStats()

  return (
    <div className="flex flex-col gap-12">
      <header className="flex max-w-2xl flex-col gap-3">
        <h1 className="text-4xl font-semibold tracking-tight">Summary</h1>
        <p className="text-muted-foreground">
          Every number on this site, what it means and how it is counted. Read{' '}
          <Link to="/methodology" className="underline underline-offset-4">
            the methodology
          </Link>{' '}
          for how repos are matched to the chain.
        </p>
      </header>

      <section className="flex flex-col gap-4">
        <h2 className="text-2xl font-semibold tracking-tight">The numbers</h2>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {STAT_DEFINITIONS.map(({ key, label, meaning, counted }) => (
            <Card key={key}>
              <CardHeader>
                <span className="text-sm text-muted-foreground">{label}</span>
                {stats ? (
                  <CardTitle className="text-4xl font-semibold">
                    {formatNumber(stats[key])}
                  </CardTitle>
                ) : (
                  <Skeleton className="h-10 w-24" />
                )}
              </CardHeader>
              <CardContent className="flex flex-col gap-2 text-sm">
                <p>{meaning}</p>
                <p className="text-muted-foreground">
                  <span className="font-medium text-foreground">Counted as:</span> {counted}
                </p>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      <section className="grid gap-4 lg:grid-cols-2">
        <ActivityChart />
        <CountryChart />
      </section>

      <section className="flex flex-col gap-4">
        <h2 className="text-2xl font-semibold tracking-tight">How confident we are</h2>
        <p className="max-w-2xl text-muted-foreground">
          Every project gets one evidence tier. The site shows the strict tiers by default.
        </p>
        <div className="overflow-x-auto rounded-lg border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Tier</TableHead>
                <TableHead>What it requires</TableHead>
                <TableHead>Shown by default</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {TIER_DEFINITIONS.map(({ tier, label, rule, strict }) => (
                <TableRow key={tier}>
                  <TableCell>
                    <Badge variant={tier === 'verified' ? 'default' : 'secondary'}>{label}</Badge>
                  </TableCell>
                  <TableCell>{rule}</TableCell>
                  <TableCell>{strict ? 'Yes' : 'No'}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </section>

      <section className="flex flex-col gap-4">
        <h2 className="text-2xl font-semibold tracking-tight">What this cannot see</h2>
        <ul className="ml-5 list-disc space-y-2 text-muted-foreground">
          {LIMITS.map((limit) => (
            <li key={limit}>{limit}</li>
          ))}
        </ul>
      </section>

      <section className="flex flex-col gap-4">
        <h2 className="text-2xl font-semibold tracking-tight">Download the data</h2>
        <p className="max-w-2xl text-muted-foreground">
          The strict projects with their chain evidence, in a schema built for directories. Every
          file validates against the published JSON Schema.
        </p>
        <div className="flex flex-wrap gap-3">
          {DOWNLOADS.map(({ label, href }) => (
            <Button key={href} variant="outline" render={<a href={href} download />}>
              <DownloadIcon />
              {label}
            </Button>
          ))}
        </div>
      </section>
    </div>
  )
}
