import { ExternalLinkIcon } from 'lucide-react'

import { DataTable, type Column } from '@/components/data-table'
import { Badge } from '@/components/ui/badge'
import { formatNumber, shortId } from '@/lib/format'
import type { ContractState, Fact } from '@/lib/types'

function fact(key: string, value: Fact) {
  if (value === null) return null
  if (key.endsWith('timestamp') && typeof value === 'number') {
    const minutes = Math.max(0, Math.round((Date.now() / 1000 - value) / 60))
    return `${key.replace(/_?timestamp$/, '') || 'updated'} ${minutes}m ago`.trim()
  }
  const text = String(value)
  return `${key} ${text.length > 12 ? shortId(text) : text}`
}

const columns: Column<ContractState>[] = [
  {
    header: 'Contract',
    cell: (row) => (
      <div className="flex flex-col gap-1">
        <span className="font-medium">{row.name}</span>
        <span className="flex items-center gap-1.5">
          <Badge variant="outline">{row.network}</Badge>
          <Badge variant="secondary">{row.kind}</Badge>
        </span>
      </div>
    ),
  },
  {
    header: 'Live state',
    cell: (row) =>
      row.snapshot ? (
        <span className="flex flex-wrap gap-x-3 gap-y-1 font-mono text-xs text-muted-foreground">
          {Object.entries(row.snapshot.facts).map(([key, value]) => {
            const text = fact(key, value)
            return text && <span key={key}>{text}</span>
          })}
        </span>
      ) : (
        <span className="text-muted-foreground">Not observed</span>
      ),
  },
  {
    header: 'Items',
    cell: (row) =>
      row.snapshot ? (
        <span className="flex flex-wrap items-center gap-1.5">
          {formatNumber(row.snapshot.items.length)}
          {row.expired.length > 0 && (
            <Badge variant="destructive">{formatNumber(row.expired.length)} expired</Badge>
          )}
        </span>
      ) : (
        '-'
      ),
  },
  { header: 'Projects', cell: (row) => formatNumber(row.projects) },
  {
    header: 'Address',
    cell: (row) => (
      <a
        href={row.explorer_url}
        target="_blank"
        rel="noreferrer"
        className="inline-flex items-center gap-1 font-mono text-xs hover:underline"
      >
        {shortId(row.id)}
        <ExternalLinkIcon className="size-3" />
      </a>
    ),
  },
]

export function ContractTable({ contracts }: { contracts: ContractState[] }) {
  return (
    <DataTable columns={columns} rows={contracts} rowKey={(row) => row.slug} paginate={false} />
  )
}
