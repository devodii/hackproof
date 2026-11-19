import { type Column, DataTable } from '@/components/data-table'
import { Reveal } from '@/components/integration/reveal'
import { ShareBar } from '@/components/integration/share-bar'
import { Badge } from '@/components/ui/badge'
import { formatNumber } from '@/lib/format'
import type { CaptureCount, ContractState } from '@/lib/types'

interface CaptureTableProps {
  rows: CaptureCount[]
  contracts: ContractState[]
}

export function CaptureTable({ rows, contracts }: CaptureTableProps) {
  const max = Math.max(...rows.map((row) => row.projects), 1)
  const tracked = rows.some((row) => row.offered_by.length || row.expired_on.length)
  const name = (slug: string) => {
    const contract = contracts.find((item) => item.slug === slug)
    return contract ? `${contract.name} · ${contract.network}` : slug
  }
  const columns: Column<CaptureCount>[] = [
    { header: 'Value', cell: (row) => <span className="font-mono">{row.value}</span> },
    {
      header: 'Projects',
      className: 'text-right tabular-nums',
      cell: (row) => formatNumber(row.projects),
    },
    { header: 'Share', cell: (row) => <ShareBar value={row.projects} max={max} /> },
    ...(tracked
      ? [
          {
            header: 'Offered by',
            cell: (row: CaptureCount) => (
              <span className="flex flex-wrap gap-1.5">
                {row.offered_by.map((slug) => (
                  <Badge key={slug} variant="outline">
                    {name(slug)}
                  </Badge>
                ))}
                {row.expired_on.map((slug) => (
                  <Badge key={slug} variant="destructive">
                    Expired on {name(slug)}
                  </Badge>
                ))}
                {!row.offered_by.length && !row.expired_on.length && (
                  <Badge variant="destructive">Not offered</Badge>
                )}
              </span>
            ),
          },
        ]
      : []),
  ]

  return (
    <Reveal>
      <DataTable columns={columns} rows={rows} rowKey={(row) => row.value} paginate={false} />
    </Reveal>
  )
}
