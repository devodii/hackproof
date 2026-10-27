import { useState } from 'react'

import { type Column, DataTable } from '@/components/data-table'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { usePagedList } from '@/hooks/use-paged-list'

interface ResourceTableProps<T> {
  resource: string
  search: string
  columns: Column<T>[]
  rowKey: (row: T) => string
  empty: string
  tiers?: readonly string[]
}

export function ResourceTable<T>({
  resource,
  search,
  columns,
  rowKey,
  empty,
  tiers,
}: ResourceTableProps<T>) {
  const [page, setPage] = useState(0)
  const { data, isPending, isError } = usePagedList<T>(resource, search, page, tiers)

  if (isError) {
    return (
      <Alert variant="destructive">
        <AlertTitle>Could not load {resource}</AlertTitle>
        <AlertDescription>The API is unreachable. Try again in a moment.</AlertDescription>
      </Alert>
    )
  }

  return (
    <DataTable
      columns={columns}
      rows={data?.items ?? []}
      total={data?.total ?? 0}
      page={page}
      onPageChange={setPage}
      rowKey={rowKey}
      isLoading={isPending}
      empty={empty}
    />
  )
}
