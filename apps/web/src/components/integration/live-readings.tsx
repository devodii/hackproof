import { type Column, DataTable } from '@/components/data-table'
import { Badge } from '@/components/ui/badge'
import type { ContractState, Reading } from '@/lib/types'

function amount(value: string) {
  const number = Number(value)
  const digits = number >= 100 ? 2 : number >= 1 ? 4 : 6
  return number.toLocaleString('en-US', { maximumFractionDigits: digits })
}

function age(seconds: number) {
  return seconds < 90 ? `${seconds}s ago` : `${Math.round(seconds / 60)}m ago`
}

interface LiveReadingsProps {
  readings: Reading[] | undefined
  contracts: ContractState[]
}

export function LiveReadings({ readings, contracts }: LiveReadingsProps) {
  const feed = (reading: Reading) => contracts.find((item) => item.slug === reading.contract)
  const columns: Column<Reading>[] = [
    {
      header: 'Asset',
      cell: (row) => <span className="font-mono font-semibold">{row.subject}</span>,
    },
    {
      header: 'Price',
      className: 'text-right tabular-nums',
      cell: (row) => (row.value === null ? '-' : amount(row.value)),
    },
    {
      header: 'Status',
      cell: (row) =>
        row.value === null ? (
          <Badge variant="destructive">No quote</Badge>
        ) : (
          row.stale !== null && (
            <Badge variant={row.stale ? 'destructive' : 'outline'}>
              {row.stale ? 'Stale' : 'Fresh'}
            </Badge>
          )
        ),
    },
    {
      header: 'Feed',
      cell: (row) => `${feed(row)?.name} · ${feed(row)?.network}`,
    },
    {
      header: 'Updated',
      cell: (row) =>
        row.age_seconds !== null
          ? age(row.age_seconds)
          : feed(row)?.expired.includes(row.subject)
            ? 'expired'
            : '-',
    },
  ]

  return (
    <DataTable
      columns={columns}
      rows={readings ?? []}
      rowKey={(row) => `${row.contract}:${row.subject}`}
      isLoading={!readings}
      paginate={false}
    />
  )
}
