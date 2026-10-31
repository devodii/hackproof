import { useEffect, useMemo, useState } from 'react'
import { useLocation } from 'react-router'
import { AlertTriangleIcon, ExternalLinkIcon, SearchIcon } from 'lucide-react'

import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import { useErrors } from '@/hooks/use-errors'
import { formatNumber } from '@/lib/format'

export function ErrorsPage() {
  const { data: errors, isPending, error } = useErrors()
  const location = useLocation()
  const [search, setSearch] = useState('')
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null)

  const targetCode = location.hash.replace('#', '').toUpperCase()

  useEffect(() => {
    if (targetCode && errors) {
      const el = document.getElementById(targetCode)
      if (el) {
        el.scrollIntoView({ behavior: 'smooth', block: 'center' })
      }
    }
  }, [targetCode, errors])

  const categories = useMemo(() => {
    if (!errors) return []
    const set = new Set<string>()
    for (const e of errors) {
      if (e.category) set.add(e.category)
    }
    return Array.from(set).sort()
  }, [errors])

  const filteredErrors = useMemo(() => {
    if (!errors) return []
    return errors.filter((e) => {
      const matchesSearch =
        search === '' ||
        e.code.toLowerCase().includes(search.toLowerCase()) ||
        e.plain_english.toLowerCase().includes(search.toLowerCase()) ||
        e.common_cause.toLowerCase().includes(search.toLowerCase()) ||
        e.category.toLowerCase().includes(search.toLowerCase())

      const matchesCat = selectedCategory === null || e.category === selectedCategory
      return matchesSearch && matchesCat
    })
  }, [errors, search, selectedCategory])

  const totalFailures = useMemo(() => {
    if (!errors) return 0
    return errors.reduce((acc, curr) => acc + (curr.count || 0), 0)
  }, [errors])

  if (isPending) {
    return (
      <div className="flex flex-col gap-6">
        <Skeleton className="h-12 w-64" />
        <Skeleton className="h-20 w-full" />
        <Skeleton className="h-64 w-full" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="rounded-lg border border-destructive/50 p-6 text-destructive">
        <p className="font-semibold">Failed to load Soroban error taxonomy</p>
        <p className="text-sm text-muted-foreground">{error.message}</p>
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-8">
      <header className="flex flex-col gap-3">
        <div className="flex items-center gap-3">
          <div className="rounded-md bg-destructive/10 p-2 text-destructive">
            <AlertTriangleIcon className="size-6" />
          </div>
          <div>
            <h1 className="text-4xl font-heading tracking-tight">Soroban Error Taxonomy</h1>
            <p className="text-muted-foreground text-sm">
              Curated taxonomy of Soroban runtime and transaction failure codes, root causes, and
              fixes.
            </p>
          </div>
        </div>

        <div className="mt-2 flex flex-wrap gap-4 text-sm text-muted-foreground">
          <div>
            <span className="font-semibold text-foreground">{errors.length}</span> documented codes
          </div>
          <div>•</div>
          <div>
            <span className="font-semibold text-foreground">{formatNumber(totalFailures)}</span>{' '}
            total failed transactions observed
          </div>
        </div>
      </header>

      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="relative w-full max-w-sm">
          <SearchIcon className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search code, explanation, cause..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9"
          />
        </div>

        <div className="flex flex-wrap gap-1.5">
          <button
            type="button"
            onClick={() => setSelectedCategory(null)}
            className={`rounded-full px-3 py-1 text-xs transition-colors ${
              selectedCategory === null
                ? 'bg-primary text-primary-foreground font-medium'
                : 'bg-muted text-muted-foreground hover:bg-muted/80'
            }`}
          >
            All
          </button>
          {categories.map((cat) => (
            <button
              key={cat}
              type="button"
              onClick={() => setSelectedCategory(cat === selectedCategory ? null : cat)}
              className={`rounded-full px-3 py-1 text-xs transition-colors ${
                selectedCategory === cat
                  ? 'bg-primary text-primary-foreground font-medium'
                  : 'bg-muted text-muted-foreground hover:bg-muted/80'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      <div className="flex flex-col gap-4">
        {filteredErrors.map((err) => {
          const isTarget = targetCode === err.code
          return (
            <Card
              key={err.code}
              id={err.code}
              className={`transition-all duration-300 ${
                isTarget ? 'border-primary ring-2 ring-primary/40 shadow-md' : 'border-border'
              }`}
            >
              <CardHeader className="pb-3">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div className="flex items-center gap-2.5">
                    <CardTitle className="font-mono text-lg font-bold">{err.code}</CardTitle>
                    <Badge variant="outline">{err.category}</Badge>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="font-mono text-xs text-muted-foreground">
                      {err.count > 0 ? (
                        <span className="text-foreground font-semibold">
                          {formatNumber(err.count)} failed
                        </span>
                      ) : (
                        '0 failures observed'
                      )}
                    </span>
                    <a
                      href={err.docs_url}
                      target="_blank"
                      rel="noreferrer"
                      className="inline-flex items-center gap-1 text-xs text-primary hover:underline"
                    >
                      Docs <ExternalLinkIcon className="size-3" />
                    </a>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="flex flex-col gap-3 text-sm">
                <div>
                  <span className="font-semibold text-foreground">Meaning: </span>
                  <span className="text-muted-foreground">{err.plain_english}</span>
                </div>
                <div>
                  <span className="font-semibold text-foreground">Common Cause: </span>
                  <span className="text-muted-foreground">{err.common_cause}</span>
                </div>
                <div className="rounded-md bg-muted/50 p-2.5 text-xs">
                  <span className="font-semibold text-foreground">Remediation / Fix: </span>
                  <span className="text-muted-foreground">{err.fix}</span>
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>
    </div>
  )
}
