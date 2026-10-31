import { useState } from 'react'
import { useTranslation } from 'react-i18next'

import { type Column, DataTable } from '@/components/data-table'
import { ScrollBox } from '@/components/scroll-box'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { useInfiniteList } from '@/hooks/use-infinite-list'
import { usePagedList } from '@/hooks/use-paged-list'
import { usePaginationMode } from '@/hooks/use-pagination-mode'
import { posthog } from '@/lib/analytics'
import type { Page } from '@/lib/types'

interface ResourceTableProps<T> {
  resource: string
  search: string
  columns: Column<T>[]
  rowKey: (row: T) => string
  empty: string
  onRowClick?: (row: T) => void
}

function Unreachable({ resource }: { resource: string }) {
  const { t } = useTranslation()
  return (
    <Alert variant="destructive">
      <AlertTitle>{t('table.unreachableTitle', { resource })}</AlertTitle>
      <AlertDescription>{t('table.unreachableDesc')}</AlertDescription>
    </Alert>
  )
}

function ClickTable<T>({
  resource,
  search,
  columns,
  rowKey,
  empty,
  onRowClick,
}: ResourceTableProps<T>) {
  const [page, setPage] = useState(0)
  const { data, isPending, isPlaceholderData, isError } = usePagedList<T>(resource, search, page)

  if (isError) return <Unreachable resource={resource} />

  return (
    <DataTable
      columns={columns}
      rows={data?.items ?? []}
      server={{
        total: data?.total,
        page,
        onPageChange: (next) => {
          posthog.capture('list_more', { mode: 'click', resource })
          setPage(next)
        },
      }}
      rowKey={rowKey}
      isLoading={isPending}
      isRefreshing={isPlaceholderData}
      empty={empty}
      onRowClick={onRowClick}
    />
  )
}

function ScrollTable<T>({
  resource,
  search,
  columns,
  rowKey,
  empty,
  onRowClick,
}: ResourceTableProps<T>) {
  const { data, isPending, isError, hasNextPage, isFetchingNextPage, fetchNextPage } =
    useInfiniteList<T>(resource, search)

  if (isError) return <Unreachable resource={resource} />

  return (
    <ScrollBox
      hasMore={hasNextPage}
      loading={isFetchingNextPage}
      onMore={() => {
        posthog.capture('list_more', { mode: 'scroll', resource })
        void fetchNextPage()
      }}
    >
      <DataTable
        columns={columns}
        rows={data?.pages.flatMap((page: Page<T>) => page.items) ?? []}
        rowKey={rowKey}
        paginate={false}
        isLoading={isPending}
        empty={empty}
        onRowClick={onRowClick}
      />
    </ScrollBox>
  )
}

export function ResourceTable<T>(props: ResourceTableProps<T>) {
  return usePaginationMode() === 'scroll' ? <ScrollTable {...props} /> : <ClickTable {...props} />
}
