import { Button } from '@/components/ui/button'
import { PAGE_SIZE } from '@/hooks/use-paged-list'
import { formatNumber } from '@/lib/format'

interface PaginationBarProps {
  total: number
  page: number
  onPageChange: (page: number) => void
}

export function PaginationBar({ total, page, onPageChange }: PaginationBarProps) {
  const lastPage = Math.max(0, Math.ceil(total / PAGE_SIZE) - 1)

  return (
    <div className="flex items-center justify-between text-sm text-muted-foreground">
      <span>{formatNumber(total)} results</span>
      <div className="flex items-center gap-2">
        <Button
          variant="outline"
          size="sm"
          disabled={page === 0}
          onClick={() => onPageChange(page - 1)}
        >
          Previous
        </Button>
        <span className="tabular-nums">
          {page + 1} / {lastPage + 1}
        </span>
        <Button
          variant="outline"
          size="sm"
          disabled={page >= lastPage}
          onClick={() => onPageChange(page + 1)}
        >
          Next
        </Button>
      </div>
    </div>
  )
}
