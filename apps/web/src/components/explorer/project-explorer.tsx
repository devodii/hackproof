import { SlidersHorizontalIcon } from 'lucide-react'
import { useMemo, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useNavigate, useSearchParams } from 'react-router'

import { DataTable } from '@/components/data-table'
import { PaginationBar } from '@/components/pagination-bar'
import { ScrollBox } from '@/components/scroll-box'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from '@/components/ui/sheet'
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { PAGE_SIZE } from '@/hooks/use-paged-list'
import { usePaginationMode } from '@/hooks/use-pagination-mode'
import { useIntegrations, useProjects } from '@/hooks/use-projects'
import { posthog } from '@/lib/analytics'
import { formatNumber } from '@/lib/format'

import { projectColumns } from './columns'
import { FilterPanel } from './filter-panel'
import { type FilterKey, matches, readSelection, selectedCount } from './filters'
import { ProjectCard } from './project-card'
import { ProjectCardSkeleton } from './project-card-skeleton'

const PLACE_RANK = { first: 0, 'runner-up': 1, none: 2 } as const

export function ProjectExplorer({ search }: { search: string }) {
  const [params, setParams] = useSearchParams()
  const [page, setPage] = useState(0)
  const navigate = useNavigate()
  const { data: projects, isPending, isError } = useProjects()
  const { data: integrations = [] } = useIntegrations()
  const view = params.get('view') === 'table' ? 'table' : 'cards'
  const selection = useMemo(() => readSelection(params), [params])
  const active = selectedCount(selection)
  const { t } = useTranslation()

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
      (projects ?? [])
        .filter(
          (project) =>
            matches(project, selection) &&
            (!needle ||
              project.project_id.toLowerCase().includes(needle) ||
              project.description?.toLowerCase().includes(needle)),
        )
        .sort((a, b) => PLACE_RANK[a.award ?? 'none'] - PLACE_RANK[b.award ?? 'none']),
    [projects, selection, needle],
  )

  const paginationMode = usePaginationMode()
  const paged =
    paginationMode === 'scroll'
      ? filtered.slice(0, (page + 1) * PAGE_SIZE)
      : filtered.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE)

  if (isError) {
    return (
      <Alert variant="destructive">
        <AlertTitle>{t('table.unreachableTitle', { resource: t('explorer.tabs.projects') })}</AlertTitle>
        <AlertDescription>{t('table.unreachableDesc')}</AlertDescription>
      </Alert>
    )
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <Sheet>
            <SheetTrigger
              render={
                <Button variant="outline" size="sm" className="gap-2 lg:hidden">
                  <SlidersHorizontalIcon className="size-4" />
                  {t('explorer.filters')} {active > 0 && `(${active})`}
                </Button>
              }
            />
            <SheetContent side="left" className="w-80 overflow-y-auto">
              <SheetHeader>
                <SheetTitle>{t('explorer.filters')}</SheetTitle>
              </SheetHeader>
              <div className="py-4">
                <FilterPanel
                  projects={projects ?? []}
                  integrations={integrations}
                  selection={selection}
                  onToggle={toggle}
                  onClear={clear}
                />
              </div>
            </SheetContent>
          </Sheet>
          <span className="text-sm text-muted-foreground tabular-nums">
            {formatNumber(filtered.length)} {t('table.resultsCount', { count: filtered.length }).replace(`${filtered.length} `, '')}
          </span>
        </div>

        <Tabs
          value={view}
          onValueChange={(next) => update((searchParams) => searchParams.set('view', next))}
        >
          <TabsList>
            <TabsTrigger value="cards">{t('explorer.cards')}</TabsTrigger>
            <TabsTrigger value="table">{t('explorer.table')}</TabsTrigger>
          </TabsList>
        </Tabs>
      </div>

      <div className="grid grid-cols-1 gap-8 lg:grid-cols-4">
        <aside className="hidden lg:block">
          <FilterPanel
            projects={projects ?? []}
            integrations={integrations}
            selection={selection}
            onToggle={toggle}
            onClear={clear}
          />
        </aside>

        <section className="lg:col-span-3">
          {isPending ? (
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
              {Array.from({ length: 9 }).map((_, index) => (
                <ProjectCardSkeleton key={index} />
              ))}
            </div>
          ) : filtered.length === 0 ? (
            <div className="rounded-lg border border-dashed py-16 text-center text-sm text-muted-foreground">
              {t('explorer.noProjects')}
            </div>
          ) : view === 'cards' ? (
            paginationMode === 'scroll' ? (
              <ScrollBox
                hasMore={paged.length < filtered.length}
                loading={false}
                onMore={() => {
                  posthog.capture('list_more', { mode: 'scroll', resource: 'projects' })
                  setPage((p) => p + 1)
                }}
              >
                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
                  {paged.map((project) => (
                    <ProjectCard key={project.project_id} project={project} />
                  ))}
                </div>
              </ScrollBox>
            ) : (
              <div className="flex flex-col gap-6">
                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
                  {paged.map((project) => (
                    <ProjectCard key={project.project_id} project={project} />
                  ))}
                </div>
                <PaginationBar
                  total={filtered.length}
                  page={page}
                  onPageChange={(next) => {
                    posthog.capture('list_more', { mode: 'click', resource: 'projects' })
                    setPage(next)
                  }}
                />
              </div>
            )
          ) : (
            <DataTable
              columns={projectColumns}
              rows={filtered}
              rowKey={(row) => row.project_id}
              onRowClick={(row) => navigate(`/project/${row.project_id}`)}
            />
          )}
        </section>
      </div>
    </div>
  )
}
