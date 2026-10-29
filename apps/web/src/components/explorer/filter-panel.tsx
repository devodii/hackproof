import { useState } from 'react'

import { Button } from '@/components/ui/button'
import { Checkbox } from '@/components/ui/checkbox'
import { countryName, flagEmoji, tierLabel } from '@/lib/format'
import type { Integration, Project } from '@/lib/types'

import { countValues, type FilterKey, type Selection, selectedCount } from './filters'

const VISIBLE = 8

interface Option {
  value: string
  label: string
  count: number
  hint?: string
}

interface FilterPanelProps {
  projects: Project[]
  integrations: Integration[]
  selection: Selection
  onToggle: (key: FilterKey, value: string) => void
  onClear: () => void
}

const FIXED: Record<'tier' | 'track' | 'activity', [string, string][]> = {
  tier: [
    ['verified', tierLabel.verified],
    ['likely', tierLabel.likely],
  ],
  track: [
    ['genesis', 'Genesis'],
    ['scale', 'Scale'],
  ],
  activity: [
    ['contracts', 'Deployed contracts'],
    ['failed', 'Failed transactions'],
  ],
}

function options(
  key: FilterKey,
  projects: Project[],
  integrations: Integration[],
  selection: Selection,
): Option[] {
  const counts = countValues(projects, selection, key)
  const chosen = new Set(selection[key])
  const labelled: [string, string, string?][] =
    key === 'tier' || key === 'track' || key === 'activity'
      ? FIXED[key].map(([value, label]) => [value, label])
      : key === 'partner'
        ? integrations.map((item) => [item.slug, item.name, item.category])
        : [
            ...new Set(
              projects.flatMap(
                (project) => (key === 'language' ? project.language : project.country) ?? [],
              ),
            ),
          ].map((value) => [
            value,
            key === 'country' ? `${flagEmoji(value)} ${countryName(value)}` : value,
          ])
  return labelled
    .map(([value, label, hint]) => ({ value, label, hint, count: counts.get(value) ?? 0 }))
    .filter((option) => option.count > 0 || chosen.has(option.value))
    .sort((a, b) => b.count - a.count || a.label.localeCompare(b.label))
}

function Group({
  title,
  items,
  chosen,
  onToggle,
  collapsible,
}: {
  title: string
  items: Option[]
  chosen: string[]
  onToggle: (value: string) => void
  collapsible: boolean
}) {
  const [expanded, setExpanded] = useState(false)
  if (items.length === 0) return null
  const shown = collapsible && !expanded ? items.slice(0, VISIBLE) : items

  return (
    <fieldset className="flex flex-col gap-2">
      <legend className="mb-1 text-sm font-medium">{title}</legend>
      {shown.map((item) => (
        <label key={item.value} className="flex cursor-pointer items-center gap-2 text-sm">
          <Checkbox
            checked={chosen.includes(item.value)}
            className="border-muted-foreground/60 dark:bg-transparent"
            onCheckedChange={() => onToggle(item.value)}
          />
          <span className="min-w-0 flex-1 truncate">{item.label}</span>
          <span className="text-xs text-muted-foreground tabular-nums">{item.count}</span>
        </label>
      ))}
      {collapsible && items.length > VISIBLE && (
        <button
          type="button"
          onClick={() => setExpanded(!expanded)}
          className="self-start text-xs text-muted-foreground hover:text-foreground"
        >
          {expanded ? 'Show less' : `Show all ${items.length}`}
        </button>
      )}
    </fieldset>
  )
}

const GROUPS: { key: FilterKey; title: string; collapsible: boolean }[] = [
  { key: 'tier', title: 'Evidence', collapsible: false },
  { key: 'track', title: 'Track', collapsible: false },
  { key: 'partner', title: 'Integrations', collapsible: true },
  { key: 'activity', title: 'On-chain activity', collapsible: false },
  { key: 'language', title: 'Language', collapsible: true },
  { key: 'country', title: 'Country', collapsible: true },
]

export function FilterPanel({
  projects,
  integrations,
  selection,
  onToggle,
  onClear,
}: FilterPanelProps) {
  const active = selectedCount(selection)

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <h2 className="font-heading text-lg">Filters</h2>
        {active > 0 && (
          <Button variant="ghost" size="sm" onClick={onClear}>
            Clear {active}
          </Button>
        )}
      </div>
      {GROUPS.map(({ key, title, collapsible }) => (
        <Group
          key={key}
          title={title}
          items={options(key, projects, integrations, selection)}
          chosen={selection[key]}
          onToggle={(value) => onToggle(key, value)}
          collapsible={collapsible}
        />
      ))}
    </div>
  )
}
