import { Fragment, type ReactNode, useState } from 'react'

import { PaginationBar } from '@/components/pagination-bar'
import { CardSkeletons, TableSkeletonRows } from '@/components/table-skeleton'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { PAGE_SIZE } from '@/hooks/use-paged-list'
import { cn } from '@/lib/utils'

function isInteractive(target: EventTarget) {
  return target instanceof Element && target.closest('a, button') !== null
}

export interface Column<T> {
  header: string
  cell: (row: T) => ReactNode
  className?: string
}

interface ServerPaging {
  total: number | undefined
  page: number
  onPageChange: (page: number) => void
}

interface DataTableProps<T> {
  columns: Column<T>[]
  rows: T[]
  rowKey: (row: T) => string
  server?: ServerPaging
  isLoading?: boolean
  isRefreshing?: boolean
  empty?: string
  onRowClick?: (row: T) => void
}

interface RowCardProps<T> {
  columns: Column<T>[]
  row: T
  onRowClick?: (row: T) => void
}

function RowCard<T>({ columns, row, onRowClick }: RowCardProps<T>) {
  const [title, ...details] = columns

  return (
    <li
      className={cn(
        'flex flex-col gap-2.5 rounded-lg border bg-card p-3',
        onRowClick && 'cursor-pointer active:bg-muted',
      )}
      tabIndex={onRowClick ? 0 : undefined}
      onClick={onRowClick ? (event) => !isInteractive(event.target) && onRowClick(row) : undefined}
      onKeyDown={
        onRowClick
          ? (event) =>
              event.key === 'Enter' && event.target === event.currentTarget && onRowClick(row)
          : undefined
      }
    >
      <div className="min-w-0">{title.cell(row)}</div>
      <dl className="grid grid-cols-[auto_1fr] items-center gap-x-4 gap-y-1.5 text-sm">
        {details.map((column) => (
          <Fragment key={column.header}>
            <dt className="text-muted-foreground">{column.header}</dt>
            <dd className="min-w-0 text-right break-words">{column.cell(row)}</dd>
          </Fragment>
        ))}
      </dl>
    </li>
  )
}

export function DataTable<T>({
  columns,
  rows,
  rowKey,
  server,
  isLoading = false,
  isRefreshing = false,
  empty = 'Nothing here.',
  onRowClick,
}: DataTableProps<T>) {
  const [localPage, setLocalPage] = useState(0)
  const paging = server ?? { total: rows.length, page: localPage, onPageChange: setLocalPage }
  const visible = server ? rows : rows.slice(paging.page * PAGE_SIZE, (paging.page + 1) * PAGE_SIZE)

  return (
    <div className="flex flex-col gap-3">
      <div
        className={cn(
          'hidden overflow-x-auto rounded-lg border transition-opacity md:block',
          isRefreshing && 'opacity-50',
        )}
      >
        <Table>
          <TableHeader>
            <TableRow>
              {columns.map((column) => (
                <TableHead key={column.header} className={column.className}>
                  {column.header}
                </TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              <TableSkeletonRows columns={columns} />
            ) : (
              visible.map((row) => (
                <TableRow
                  key={rowKey(row)}
                  className={cn(onRowClick && 'cursor-pointer')}
                  tabIndex={onRowClick ? 0 : undefined}
                  onClick={
                    onRowClick
                      ? (event) => !isInteractive(event.target) && onRowClick(row)
                      : undefined
                  }
                  onKeyDown={
                    onRowClick
                      ? (event) =>
                          event.key === 'Enter' &&
                          event.target === event.currentTarget &&
                          onRowClick(row)
                      : undefined
                  }
                >
                  {columns.map((column) => (
                    <TableCell key={column.header} className={cn(column.className)}>
                      {column.cell(row)}
                    </TableCell>
                  ))}
                </TableRow>
              ))
            )}
            {!isLoading && visible.length === 0 && (
              <TableRow>
                <TableCell
                  colSpan={columns.length}
                  className="h-24 text-center text-muted-foreground"
                >
                  {empty}
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
      <ul
        className={cn(
          'flex flex-col gap-2 transition-opacity md:hidden',
          isRefreshing && 'opacity-50',
        )}
      >
        {isLoading ? (
          <CardSkeletons rows={columns.length} />
        ) : visible.length === 0 ? (
          <li className="rounded-lg border p-6 text-center text-sm text-muted-foreground">
            {empty}
          </li>
        ) : (
          visible.map((row) => (
            <RowCard key={rowKey(row)} columns={columns} row={row} onRowClick={onRowClick} />
          ))
        )}
      </ul>
      {!isLoading && <PaginationBar {...paging} />}
    </div>
  )
}
