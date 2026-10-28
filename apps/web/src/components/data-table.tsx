import { type ReactNode, useState } from 'react'

import { PaginationBar } from '@/components/pagination-bar'
import { Skeleton } from '@/components/ui/skeleton'
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

const SKELETON_ROWS = 8
const SKELETON_WIDTHS = ['w-28', 'w-40', 'w-24', 'w-36', 'w-32']

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
          'overflow-x-auto rounded-lg border transition-opacity',
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
            {isLoading
              ? Array.from({ length: SKELETON_ROWS }, (_, rowIndex) => (
                  <TableRow key={rowIndex} className="h-[3.1rem] hover:bg-transparent">
                    {columns.map((column, columnIndex) => (
                      <TableCell key={column.header}>
                        <Skeleton
                          className={cn(
                            'h-4',
                            column.className?.includes('text-right')
                              ? 'ml-auto w-10'
                              : SKELETON_WIDTHS[
                                  (rowIndex * 2 + columnIndex) % SKELETON_WIDTHS.length
                                ],
                          )}
                          style={{ animationDelay: `${rowIndex * 90 + columnIndex * 40}ms` }}
                        />
                      </TableCell>
                    ))}
                  </TableRow>
                ))
              : visible.map((row) => (
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
                ))}
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
      {!isLoading && <PaginationBar {...paging} />}
    </div>
  )
}
