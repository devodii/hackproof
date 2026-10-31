import { LayersIcon, WrenchIcon } from 'lucide-react'

import { DistributionBar } from '@/components/charts/distribution-bar'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { useTooling } from '@/hooks/use-tooling'

export function ToolingPage() {
  const { data, isPending, error } = useTooling()

  if (isPending) {
    return (
      <div className="flex flex-col gap-8 py-6">
        <div className="flex flex-col gap-2">
          <Skeleton className="h-10 w-64" />
          <Skeleton className="h-5 w-96" />
        </div>
        <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
          {Array.from({ length: 4 }).map((_, i) => (
            <Card key={i}>
              <CardHeader>
                <Skeleton className="h-6 w-48" />
                <Skeleton className="h-4 w-72" />
              </CardHeader>
              <CardContent>
                <Skeleton className="h-32 w-full" />
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    )
  }

  if (error || !data) {
    return (
      <div className="flex flex-col items-center justify-center gap-4 py-16 text-center">
        <WrenchIcon className="size-12 text-muted-foreground/50" />
        <h2 className="text-xl font-semibold">Unable to load tooling adoption stats</h2>
        <p className="text-sm text-muted-foreground">
          {error instanceof Error ? error.message : 'Please check your connection or try again.'}
        </p>
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-8 py-6">
      <header className="flex flex-col gap-3">
        <div className="flex items-center gap-3">
          <div className="flex size-10 items-center justify-center rounded-lg border bg-muted/30">
            <LayersIcon className="size-5 text-foreground" />
          </div>
          <div>
            <h1 className="text-3xl font-bold tracking-tight sm:text-4xl">Tooling Adoption</h1>
            <p className="text-sm text-muted-foreground sm:text-base">
              What does the winning stack look like? Adoption rates across{' '}
              <span className="font-semibold text-foreground">{data.total_projects}</span> verified
              and likely hackathon projects.
            </p>
          </div>
        </div>
      </header>

      <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
        {data.categories.map((group) => (
          <Card key={group.category} className="flex flex-col justify-between">
            <CardHeader className="pb-4">
              <CardTitle className="text-lg">{group.category}</CardTitle>
              <CardDescription>{group.description}</CardDescription>
            </CardHeader>
            <CardContent>
              {group.items.length > 0 ? (
                <DistributionBar items={group.items} maxCount={data.total_projects} />
              ) : (
                <p className="py-4 text-center text-xs text-muted-foreground">
                  No packages detected yet in this category.
                </p>
              )}
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
