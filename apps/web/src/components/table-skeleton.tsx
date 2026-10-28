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

export function TableSkeleton({ columns, rows }: { columns: number; rows?: number }) {
  const placeholders = Array.from({ length: columns }, (_, index) => ({ header: String(index) }))

  return (
    <div className="overflow-hidden rounded-lg border">
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
  )
}
