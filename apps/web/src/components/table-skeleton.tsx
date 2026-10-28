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

const WIDTHS = ['w-28', 'w-40', 'w-24', 'w-36', 'w-32']

interface SkeletonColumn {
  header: string
  className?: string
}

interface TableSkeletonRowsProps {
  columns: SkeletonColumn[]
  rows?: number
}

export function TableSkeletonRows({ columns, rows = 8 }: TableSkeletonRowsProps) {
  return Array.from({ length: rows }, (_, rowIndex) => (
    <TableRow key={rowIndex} className="h-[3.1rem] hover:bg-transparent">
      {columns.map((column, columnIndex) => (
        <TableCell key={column.header}>
          <Skeleton
            className={cn(
              'h-4',
              column.className?.includes('text-right')
                ? 'ml-auto w-10'
                : WIDTHS[(rowIndex * 2 + columnIndex) % WIDTHS.length],
            )}
            style={{ animationDelay: `${rowIndex * 90 + columnIndex * 40}ms` }}
          />
        </TableCell>
      ))}
    </TableRow>
  ))
}

export function CardSkeletons({ rows, count = 5 }: { rows: number; count?: number }) {
  return Array.from({ length: count }, (_, cardIndex) => (
    <li key={cardIndex} className="flex flex-col gap-3 rounded-lg border bg-card p-3">
      <Skeleton className="h-4 w-2/5" style={{ animationDelay: `${cardIndex * 90}ms` }} />
      {Array.from({ length: Math.min(rows - 1, 3) }, (_, rowIndex) => (
        <div key={rowIndex} className="flex items-center justify-between gap-6">
          <Skeleton className="h-3.5 w-16" style={{ animationDelay: `${cardIndex * 90}ms` }} />
          <Skeleton className="h-3.5 w-24" style={{ animationDelay: `${cardIndex * 90}ms` }} />
        </div>
      ))}
    </li>
  ))
}

export function TableSkeleton({ columns, rows }: { columns: number; rows?: number }) {
  const placeholders = Array.from({ length: columns }, (_, index) => ({ header: String(index) }))

  return (
    <>
      <ul className="flex flex-col gap-2 md:hidden">
        <CardSkeletons rows={columns} count={4} />
      </ul>
      <div className="hidden overflow-hidden rounded-lg border md:block">
        <Table>
          <TableHeader>
            <TableRow>
              {placeholders.map(({ header }) => (
                <TableHead key={header}>
                  <Skeleton className="h-4 w-16" />
                </TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            <TableSkeletonRows columns={placeholders} rows={rows} />
          </TableBody>
        </Table>
      </div>
    </>
  )
}
