import type { ReactNode } from 'react'

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
import { cn } from '@/lib/utils'

export interface Column<T> {
  header: string
  cell: (row: T) => ReactNode
  className?: string
}

interface DataTableProps<T> {
  columns: Column<T>[]
  rows: T[]
  total: number | undefined
  page: number
  onPageChange: (page: number) => void
  rowKey: (row: T) => string
  isLoading?: boolean
  isRefreshing?: boolean
  empty?: string
}

export function DataTable<T>({
  columns,
  rows,
  total,
  page,
  onPageChange,
  rowKey,
  isLoading = false,
  isRefreshing = false,
  empty = 'Nothing here.',
}: DataTableProps<T>) {
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
              ? Array.from({ length: 6 }, (_, index) => (
                  <TableRow key={index}>
                    {columns.map((column) => (
                      <TableCell key={column.header}>
                        <Skeleton className="h-4 w-full max-w-32" />
                      </TableCell>
                    ))}
                  </TableRow>
                ))
              : rows.map((row) => (
                  <TableRow key={rowKey(row)}>
                    {columns.map((column) => (
                      <TableCell key={column.header} className={cn(column.className)}>
                        {column.cell(row)}
                      </TableCell>
                    ))}
                  </TableRow>
                ))}
            {!isLoading && rows.length === 0 && (
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
      <PaginationBar total={total} page={page} onPageChange={onPageChange} />
    </div>
  )
}
