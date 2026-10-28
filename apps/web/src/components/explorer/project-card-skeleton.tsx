import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'

export function ProjectCardSkeleton({ delay = 0 }: { delay?: number }) {
  const stagger = { animationDelay: `${delay}ms` }

  return (
    <Card size="sm" className="h-full">
      <CardHeader>
        <div className="flex items-start gap-3">
          <Skeleton className="size-8 shrink-0 rounded-full" style={stagger} />
          <div className="flex flex-1 flex-col gap-2">
            <Skeleton className="h-4 w-2/3" style={stagger} />
            <Skeleton className="h-5 w-24" style={stagger} />
          </div>
        </div>
      </CardHeader>
      <CardContent className="flex flex-col gap-3">
        <div className="flex flex-col gap-2">
          <Skeleton className="h-3.5 w-full" style={stagger} />
          <Skeleton className="h-3.5 w-4/5" style={stagger} />
        </div>
        <div className="flex gap-3">
          <Skeleton className="h-3 w-16" style={stagger} />
          <Skeleton className="h-3 w-20" style={stagger} />
        </div>
      </CardContent>
    </Card>
  )
}
