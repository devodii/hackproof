import { DataTable, type Column } from '@/components/data-table'
import { SeverityIcon } from '@/components/integration/check-status'
import { formatNumber } from '@/lib/format'
import type { CheckCount } from '@/lib/types'

const columns: Column<CheckCount>[] = [
  {
    header: 'Check',
    cell: (row) => (
      <span className="flex items-center gap-2">
        <SeverityIcon severity={row.severity} />
        {row.label}
      </span>
    ),
  },
  { header: 'Passing', cell: (row) => formatNumber(row.passing) },
  { header: 'Failing', cell: (row) => formatNumber(row.failing) },
]

export function CheckTable({ checks }: { checks: CheckCount[] }) {
  return <DataTable columns={columns} rows={checks} rowKey={(row) => row.slug} paginate={false} />
}
