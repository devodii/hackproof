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
import moment from 'moment'
import { useState } from 'react'

import { type Column, DataTable } from '@/components/data-table'
import { Reveal } from '@/components/integration/reveal'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
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

const FRESH_HOURS = 36

function factValue(value: Fact | undefined) {
  if (value === undefined || value === null) return '-'
  return typeof value === 'number' ? formatNumber(value) : value
}

function tone(value: Fact | undefined) {
  if (value === 'yes') return 'text-ok'
  if (value === 'no') return 'text-destructive'
  return ''
}

function isFresh(iso: string | null) {
  return iso !== null && moment().diff(moment(iso), 'hours') < FRESH_HOURS
}

function columnsFor(
  kind: string,
  surfaces: ContractState[],
  onItems: (surface: ContractState) => void,
): Column<ContractState>[] {
  const Icon = KIND_ICON[kind] ?? BoxIcon
  const keys = [...new Set(surfaces.flatMap((item) => Object.keys(item.snapshot?.facts ?? {})))]

  return [
    {
      header: 'Surface',
      cell: (row) => (
        <span className="flex items-center gap-2.5">
          <Icon className="size-4 shrink-0 text-primary" />
          <span className="flex flex-col">
            <span className="font-medium">{row.name}</span>
            <span className="font-mono text-xs text-muted-foreground">
              {shortId(row.id.replace(/^https?:\/\//, ''), 24, 8)}
            </span>
          </span>
        </span>
      ),
    },
    { header: 'Network', cell: (row) => <Badge variant="outline">{row.network}</Badge> },
    ...keys.map((key) => ({
      header: humanize(key),
      cell: (row: ContractState) => {
        const value = row.snapshot?.facts[key]
        return (
          <span
            className={cn('block max-w-48 truncate tabular-nums', tone(value))}
            title={String(value)}
          >
            {factValue(value)}
          </span>
        )
      },
    })),
    {
      header: 'Items',
      cell: (row) =>
        row.snapshot && row.snapshot.items.length > 0 ? (
          <button
            type="button"
            onClick={() => onItems(row)}
            className="underline decoration-primary underline-offset-4 hover:decoration-2"
          >
            {formatNumber(row.snapshot.items.length)}
          </button>
        ) : (
          '-'
        ),
    },
    {
      header: 'Read',
      cell: (row) => (
        <span className="flex items-center gap-1.5 whitespace-nowrap text-muted-foreground">
          <span
            className={cn(
              'size-2 rounded-full',
              isFresh(row.observed_at) ? 'bg-ok' : 'bg-muted-foreground/40',
            )}
          />
          {row.observed_at ? moment(row.observed_at).fromNow() : 'not yet'}
        </span>
      ),
    },
    {
      header: '',
      cell: (row) => (
        <a
          href={row.explorer_url}
          target="_blank"
          rel="noreferrer"
          aria-label={`Open ${row.name}`}
          className="text-muted-foreground hover:text-foreground"
        >
          <ExternalLinkIcon className="size-3.5" />
        </a>
      ),
    },
  ]
}

function Group({ kind, items }: { kind: string; items: ContractState[] }) {
  const [open, setOpen] = useState<ContractState | null>(null)

  return (
    <Reveal className="flex flex-col gap-3">
      <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
        {humanize(kind)}
        <Badge variant="outline">{items.length}</Badge>
      </div>
      <DataTable
        columns={columnsFor(kind, items, setOpen)}
        rows={items}
        rowKey={(row) => `${row.network}:${row.slug}`}
        paginate={false}
      />
      {open?.snapshot && (
        <div className="flex flex-col gap-2 rounded-lg border bg-card p-3">
          <div className="flex items-center justify-between text-sm">
            <span className="font-medium">
              {open.name} · {formatNumber(open.snapshot.items.length)} items
            </span>
            <Button variant="ghost" size="sm" onClick={() => setOpen(null)}>
              Close
            </Button>
          </div>
          <div className="flex max-h-48 flex-wrap gap-1.5 overflow-auto">
            {open.snapshot.items.map((item) => (
              <Badge key={item} variant="secondary" className="font-mono">
                {item}
              </Badge>
            ))}
          </div>
        </div>
      )}
    </Reveal>
  )
}

export function SurfaceTable({ surfaces }: { surfaces: ContractState[] }) {
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
