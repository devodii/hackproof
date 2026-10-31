import { useTranslation } from 'react-i18next'

import { Button } from '@/components/ui/button'
import { PAGE_SIZE } from '@/hooks/use-paged-list'
import { Skeleton } from '@/components/ui/skeleton'
import { formatNumber } from '@/lib/format'

interface PaginationBarProps {
  total: number | undefined
  page: number
  onPageChange: (page: number) => void
}

export function PaginationBar({ total, page, onPageChange }: PaginationBarProps) {
  const { t } = useTranslation()
  if (total !== undefined && total <= PAGE_SIZE) return null

  const lastPage = Math.max(0, Math.ceil((total ?? 0) / PAGE_SIZE) - 1)

  return (
    <div className="flex items-center justify-between text-sm text-muted-foreground">
      {total === undefined ? (
        <Skeleton className="h-4 w-20" />
      ) : (
        <span>{t('table.resultsCount', { count: formatNumber(total) })}</span>
      )}
      <div className="flex items-center gap-2">
        <Button
          variant="outline"
          size="sm"
          disabled={total === undefined || page === 0}
          onClick={() => onPageChange(page - 1)}
        >
          {t('table.previous')}
        </Button>
        <span className="tabular-nums">
          {page + 1} / {lastPage + 1}
        </span>
        <Button
          variant="outline"
          size="sm"
          disabled={total === undefined || page >= lastPage}
          onClick={() => onPageChange(page + 1)}
        >
          {t('table.next')}
        </Button>
      </div>
    </div>
  )
}
