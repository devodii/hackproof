import { useState } from 'react'

import { ProjectCard } from '@/components/explorer/project-card'
import { ProjectCardSkeleton } from '@/components/explorer/project-card-skeleton'
import { PaginationBar } from '@/components/pagination-bar'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { cn } from '@/lib/utils'
import { usePagedList } from '@/hooks/use-paged-list'
import type { Project } from '@/lib/types'

interface ProjectGridProps {
  search: string
  tiers?: readonly string[]
}

export function ProjectGrid({ search, tiers }: ProjectGridProps) {
  const [page, setPage] = useState(0)
  const { data, isPending, isPlaceholderData, isError } = usePagedList<Project>(
    'projects',
    search,
    page,
    tiers,
  )

  if (isError) {
    return (
      <Alert variant="destructive">
        <AlertTitle>Could not load projects</AlertTitle>
        <AlertDescription>The API is unreachable. Try again in a moment.</AlertDescription>
      </Alert>
    )
  }

  return (
    <div className="flex flex-col gap-4">
      <div
        className={cn(
          'grid gap-4 transition-opacity sm:grid-cols-2 lg:grid-cols-3',
          isPlaceholderData && 'opacity-50',
        )}
      >
        {isPending
          ? Array.from({ length: 9 }, (_, index) => (
              <ProjectCardSkeleton
                key={index}
                delay={(index % 3) * 140 + Math.floor(index / 3) * 90}
              />
            ))
          : data.items.map((project) => <ProjectCard key={project.project_id} project={project} />)}
      </div>
      {data && data.items.length === 0 && (
        <p className="py-12 text-center text-muted-foreground">No projects match.</p>
      )}
      <PaginationBar total={data?.total} page={page} onPageChange={setPage} />
    </div>
  )
}
