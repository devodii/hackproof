import { useState } from 'react'

import { Button } from '@/components/ui/button'
import { Checkbox } from '@/components/ui/checkbox'
import type { AIAgent, EcosystemTool, Integration, Project } from '@/lib/types'

import { GROUPS, type Option, options } from './filter-options'
import { type FilterKey, type Selection, selectedCount } from './filters'

const VISIBLE = 8

interface FilterPanelProps {
  projects: Project[]
  integrations: Integration[]
  tools: EcosystemTool[]
  agents: AIAgent[]
  selection: Selection
  onToggle: (key: FilterKey, value: string) => void
  onClear: () => void
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

export function FilterPanel({
  projects,
  integrations,
  tools,
  agents,
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
          items={options(key, projects, integrations, tools, agents, selection)}
          chosen={selection[key]}
          onToggle={(value) => onToggle(key, value)}
          collapsible={collapsible}
        />
      ))}
    </div>
  )
}
