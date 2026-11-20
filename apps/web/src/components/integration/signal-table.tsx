import { type Column, DataTable } from '@/components/data-table'
import { Reveal } from '@/components/integration/reveal'
import { ShareBar } from '@/components/integration/share-bar'
import { Badge } from '@/components/ui/badge'
import { formatNumber, humanize } from '@/lib/format'
import type { SignalCount } from '@/lib/types'

export function SignalTable({ signals, max }: { signals: SignalCount[]; max: number }) {
  const columns: Column<SignalCount>[] = [
    {
      header: 'Signal',
      cell: (row) => (
        <span className={row.projects ? '' : 'text-muted-foreground'}>{row.label}</span>
      ),
    },
    { header: 'Group', cell: (row) => <Badge variant="outline">{humanize(row.group)}</Badge> },
    {
      header: 'Projects',
      className: 'text-right tabular-nums',
      cell: (row) => formatNumber(row.projects),
    },
    { header: 'Share', cell: (row) => <ShareBar value={row.projects} max={max} /> },
  ]

  return (
    <Reveal>
      <DataTable columns={columns} rows={signals} rowKey={(row) => row.slug} paginate={false} />
    </Reveal>
  )
}
