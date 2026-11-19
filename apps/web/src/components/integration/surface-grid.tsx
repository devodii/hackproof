import {
  ActivityIcon,
  BoxIcon,
  CoinsIcon,
  CpuIcon,
  ExternalLinkIcon,
  GitBranchIcon,
  GlobeIcon,
  PackageIcon,
  type LucideIcon,
} from 'lucide-react'
import { useState } from 'react'

import { Reveal } from '@/components/integration/reveal'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { formatNumber, humanize, shortId } from '@/lib/format'
import type { ContractState, Fact } from '@/lib/types'
import { cn } from '@/lib/utils'

const KIND_ICON: Record<string, LucideIcon> = {
  api: GlobeIcon,
  package: PackageIcon,
  repo: GitBranchIcon,
  wasm: CpuIcon,
  feed: ActivityIcon,
  token: CoinsIcon,
}

const FACTS_SHOWN = 6
const GROUP_SHOWN = 3
const FRESH_HOURS = 36

function factValue(value: Fact) {
  if (typeof value === 'number') return formatNumber(value)
  return value ?? '-'
}

function tone(value: Fact) {
  if (value === 'yes') return 'text-ok'
  if (value === 'no') return 'text-destructive'
  return ''
}

function isFresh(iso: string | null) {
  return iso !== null && Date.now() - new Date(iso).getTime() < FRESH_HOURS * 3_600_000
}

function Pulse({ live }: { live: boolean }) {
  return (
    <span className="relative flex size-2.5 shrink-0">
      {live && (
        <span className="absolute inline-flex size-full animate-ping rounded-full bg-ok opacity-60" />
      )}
      <span
        className={cn(
          'relative inline-flex size-2.5 rounded-full',
          live ? 'bg-ok' : 'bg-muted-foreground/40',
        )}
      />
    </span>
  )
}

function SurfaceCard({ surface }: { surface: ContractState }) {
  const [open, setOpen] = useState(false)
  const Icon = KIND_ICON[surface.kind] ?? BoxIcon
  const facts = Object.entries(surface.snapshot?.facts ?? {}).slice(0, FACTS_SHOWN)
  const items = surface.snapshot?.items ?? []

  return (
    <Card className="h-full transition-shadow hover:ring-primary/40">
      <CardContent className="flex h-full flex-col gap-4">
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-center gap-3">
            <span className="flex size-9 items-center justify-center rounded-lg bg-primary/15 text-primary">
              <Icon className="size-4.5" />
            </span>
            <div className="flex flex-col">
              <span className="font-medium">{surface.name}</span>
              <span className="font-mono text-xs text-muted-foreground">
                {shortId(surface.id.replace(/^https?:\/\//, ''), 22, 8)}
              </span>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Badge variant="outline">{surface.network}</Badge>
            <Pulse live={isFresh(surface.observed_at)} />
          </div>
        </div>
        {surface.snapshot ? (
          <dl className="grid grid-cols-2 gap-x-4 gap-y-3">
            {facts.map(([key, value]) => (
              <div key={key} className="flex min-w-0 flex-col gap-0.5">
                <dt className="text-eyebrow tracking-eyebrow text-muted-foreground uppercase">
                  {humanize(key)}
                </dt>
                <dd className={cn('truncate font-heading text-xl leading-tight', tone(value))}>
                  {factValue(value)}
                </dd>
              </div>
            ))}
          </dl>
        ) : (
          <p className="text-sm text-muted-foreground">Not observed yet</p>
        )}
        {items.length > 0 && (
          <div className="flex flex-col gap-2">
            <button
              type="button"
              onClick={() => setOpen((value) => !value)}
              className="self-start text-sm text-primary hover:underline"
            >
              {open ? 'Hide' : 'Show'} {formatNumber(items.length)} items
            </button>
            {open && (
              <div className="flex max-h-48 flex-wrap gap-1.5 overflow-auto">
                {items.map((item) => (
                  <Badge key={item} variant="secondary" className="font-mono">
                    {item}
                  </Badge>
                ))}
              </div>
            )}
          </div>
        )}
        <a
          href={surface.explorer_url}
          target="_blank"
          rel="noreferrer"
          className="mt-auto inline-flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground"
        >
          Open <ExternalLinkIcon className="size-3" />
        </a>
      </CardContent>
    </Card>
  )
}

function Group({ kind, items }: { kind: string; items: ContractState[] }) {
  const [all, setAll] = useState(false)
  const shown = all ? items : items.slice(0, GROUP_SHOWN)

  return (
    <div className="flex flex-col gap-3">
      <Reveal className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
        {humanize(kind)}
        <Badge variant="outline">{items.length}</Badge>
      </Reveal>
      <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
        {shown.map((surface, index) => (
          <Reveal
            key={`${surface.network}:${surface.slug}`}
            delay={Math.min(index, 5) * 0.06}
            className="h-full"
          >
            <SurfaceCard surface={surface} />
          </Reveal>
        ))}
      </div>
      {items.length > GROUP_SHOWN && (
        <Button variant="ghost" className="self-start" onClick={() => setAll((value) => !value)}>
          {all ? 'Show fewer' : `Show all ${items.length}`}
        </Button>
      )}
    </div>
  )
}

export function SurfaceGrid({ surfaces }: { surfaces: ContractState[] }) {
  const groups = surfaces.reduce<Record<string, ContractState[]>>((found, surface) => {
    ;(found[surface.kind] ??= []).push(surface)
    return found
  }, {})

  return (
    <div className="flex flex-col gap-8">
      {Object.entries(groups).map(([kind, items]) => (
        <Group key={kind} kind={kind} items={items} />
      ))}
    </div>
  )
}
