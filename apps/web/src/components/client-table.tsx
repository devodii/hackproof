import { useState } from 'react'

import { type Column, DataTable } from '@/components/data-table'
import { PAGE_SIZE } from '@/hooks/use-paged-list'

interface ClientTableProps<T> {
  columns: Column<T>[]
  rows: T[]
  rowKey: (row: T) => string
  empty: string
}

export function ClientTable<T>({ columns, rows, rowKey, empty }: ClientTableProps<T>) {
  const [page, setPage] = useState(0)

  return (
    <DataTable
      columns={columns}
      rows={rows.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE)}
      total={rows.length}
      page={page}
      onPageChange={setPage}
      rowKey={rowKey}
      empty={empty}
    />
  )
}
