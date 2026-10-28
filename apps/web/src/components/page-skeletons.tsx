import { TableSkeleton } from '@/components/table-skeleton'
import { Skeleton } from '@/components/ui/skeleton'

function AccordionSkeleton({ closed, columns }: { closed: number; columns: number }) {
  return (
    <div className="flex flex-col">
      <div className="flex flex-col gap-4 border-b pb-6">
        <div className="flex items-center gap-3 py-4">
          <Skeleton className="h-7 w-40" />
          <Skeleton className="h-5 w-8 rounded-full" />
        </div>
        <TableSkeleton columns={columns} rows={6} />
      </div>
      {Array.from({ length: closed }, (_, index) => (
        <div key={index} className="flex items-center gap-3 border-b py-4">
          <Skeleton className="h-7 w-48" style={{ animationDelay: `${(index + 1) * 120}ms` }} />
          <Skeleton className="h-5 w-8 rounded-full" />
        </div>
      ))}
    </div>
  )
}

export function ProjectSkeleton() {
  return (
    <div className="flex flex-col gap-8">
      <header className="flex flex-col gap-3">
        <div className="flex items-center gap-3">
          <Skeleton className="size-8 shrink-0 rounded-full" />
          <Skeleton className="h-11 w-64" />
          <Skeleton className="h-5 w-20" />
        </div>
        <Skeleton className="h-4 w-full max-w-2xl" />
        <div className="flex gap-4">
          <Skeleton className="h-4 w-20" />
          <Skeleton className="h-4 w-24" />
          <Skeleton className="h-4 w-16" />
        </div>
      </header>
      <AccordionSkeleton closed={3} columns={4} />
    </div>
  )
}

export function BuilderSkeleton() {
  return (
    <div className="flex flex-col gap-8">
      <header className="flex flex-col gap-3">
        <Skeleton className="h-11 w-48" />
        <Skeleton className="h-4 w-full max-w-lg" />
      </header>
      <AccordionSkeleton closed={2} columns={6} />
    </div>
  )
}
