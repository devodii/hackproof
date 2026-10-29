import { SlidersHorizontalIcon } from 'lucide-react'
import { useMemo, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router'

import { DataTable } from '@/components/data-table'
import { PaginationBar } from '@/components/pagination-bar'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from '@/components/ui/sheet'
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { PAGE_SIZE } from '@/hooks/use-paged-list'
import { useIntegrations, useProjects } from '@/hooks/use-projects'
import { formatNumber } from '@/lib/format'
import { cn } from '@/lib/utils'

import { projectColumns } from './columns'
import { FilterPanel } from './filter-panel'
import { type FilterKey, matches, readSelection, selectedCount } from './filters'
import { ProjectCard } from './project-card'
import { ProjectCardSkeleton } from './project-card-skeleton'

export function ProjectExplorer({ search }: { search: string }) {
  const [params, setParams] = useSearchParams()
  const [page, setPage] = useState(0)
  const navigate = useNavigate()
  const { data: projects, isPending, isError } = useProjects()
  const { data: integrations = [] } = useIntegrations()
  const view = params.get('view') === 'table' ? 'table' : 'cards'
  const selection = useMemo(() => readSelection(params), [params])
  const active = selectedCount(selection)

  const update = (change: (next: URLSearchParams) => void) => {
    setPage(0)
    setParams((previous) => {
      const next = new URLSearchParams(previous)
      change(next)
      return next
    })
  }

  const toggle = (key: FilterKey, value: string) =>
    update((next) => {
      const chosen = next.getAll(key)
      next.delete(key)
      ;(chosen.includes(value)
        ? chosen.filter((item) => item !== value)
        : [...chosen, value]
      ).forEach((item) => next.append(key, item))
    })

  const clear = () => update((next) => Object.keys(selection).forEach((key) => next.delete(key)))

  const needle = search.toLowerCase()
  const filtered = useMemo(
    () =>
      (projects ?? []).filter(
        (project) =>
          matches(project, selection) &&
          (!needle ||
            project.project_id.toLowerCase().includes(needle) ||
            project.description?.toLowerCase().includes(needle)),
      ),
    [projects, selection, needle],
  )
  const visible = filtered.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE)

  const panel = (
    <FilterPanel
      projects={projects ?? []}
      integrations={integrations}
      selection={selection}
      onToggle={toggle}
      onClear={clear}
    />
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
    <div className="grid gap-6 lg:grid-cols-[15rem_minmax(0,1fr)]">
      <aside className="hidden lg:block">
        <div className="sticky top-20 max-h-[calc(100svh-6rem)] overflow-y-auto pr-2">{panel}</div>
      </aside>
      <div className="flex min-w-0 flex-col gap-4">
        <div className="flex items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <Sheet>
              <SheetTrigger render={<Button variant="outline" size="sm" className="lg:hidden" />}>
                <SlidersHorizontalIcon />
                Filters{active > 0 && ` (${active})`}
              </SheetTrigger>
              <SheetContent side="left" className="overflow-y-auto p-4">
                <SheetHeader className="sr-only">
                  <SheetTitle>Filters</SheetTitle>
                </SheetHeader>
                {panel}
              </SheetContent>
            </Sheet>
            <span className="text-sm text-muted-foreground tabular-nums">
              {isPending ? 'Loading projects' : `${formatNumber(filtered.length)} projects`}
            </span>
          </div>
          <Tabs value={view} onValueChange={(next) => update((p) => p.set('view', next))}>
            <TabsList>
              <TabsTrigger value="cards">Cards</TabsTrigger>
              <TabsTrigger value="table">Table</TabsTrigger>
            </TabsList>
          </Tabs>
        </div>
        {view === 'cards' ? (
          <div className="flex flex-col gap-4">
            <div className={cn('grid gap-4 sm:grid-cols-2 xl:grid-cols-3')}>
              {isPending
                ? Array.from({ length: 9 }, (_, index) => (
                    <ProjectCardSkeleton
                      key={index}
                      delay={(index % 3) * 140 + Math.floor(index / 3) * 90}
                    />
                  ))
                : visible.map((project) => (
                    <ProjectCard key={project.project_id} project={project} />
                  ))}
            </div>
            {!isPending && filtered.length === 0 && (
              <p className="py-12 text-center text-muted-foreground">No projects match.</p>
            )}
            <PaginationBar
              total={isPending ? undefined : filtered.length}
              page={page}
              onPageChange={setPage}
            />
          </div>
        ) : (
          <DataTable
            columns={projectColumns}
            rows={filtered}
            rowKey={(row) => row.project_id}
            isLoading={isPending}
            empty="No projects match."
            onRowClick={(row) => navigate(`/project/${row.project_id}`)}
          />
        )}
      </div>
    </div>
  )
}
