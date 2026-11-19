import { DataTable, type Column } from '@/components/data-table'
import { Badge } from '@/components/ui/badge'
import { formatNumber } from '@/lib/format'
import type { CaptureCount, ContractState } from '@/lib/types'

export function CaptureDemand({
  rows,
  contracts,
}: {
  rows: CaptureCount[]
  contracts: ContractState[]
}) {
  const columns: Column<CaptureCount>[] = [
    { header: 'Asked for', cell: (row) => <span className="font-mono">{row.value}</span> },
    { header: 'Projects', cell: (row) => formatNumber(row.projects) },
    {
      header: 'Offered by',
      cell: (row) =>
        row.offered_by.length ? (
          <span className="flex flex-wrap gap-1.5">
            {row.offered_by.map((slug) => {
              const contract = contracts.find((item) => item.slug === slug)
              return (
                <Badge key={slug} variant="outline">
                  {contract?.name} · {contract?.network}
                </Badge>
              )
            })}
          </span>
        ) : row.expired_on.length ? (
          <span className="flex flex-wrap gap-1.5">
            {row.expired_on.map((slug) => {
              const contract = contracts.find((item) => item.slug === slug)
              return (
                <Badge key={slug} variant="destructive">
                  Expired on {contract?.name} · {contract?.network}
                </Badge>
              )
            })}
          </span>
        ) : (
          <Badge variant="destructive">Not offered</Badge>
        ),
    },
  ]

  return <DataTable columns={columns} rows={rows} rowKey={(row) => row.value} paginate={false} />
}
