import { useState } from 'react'
import { useTranslation } from 'react-i18next'

import { Button } from '@/components/ui/button'
import { Checkbox } from '@/components/ui/checkbox'
import { countryName, flagEmoji, placeLabel, tierLabel, trackLabel } from '@/lib/format'
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

function options(
  key: FilterKey,
  projects: Project[],
  integrations: Integration[],
  selection: Selection,
  t: (k: string, opts?: Record<string, unknown>) => string,
): Option[] {
  const counts = countValues(projects, selection, key)
  const chosen = new Set(selection[key])

  const fixedLabels: Record<'award' | 'tier' | 'track' | 'activity', [string, string][]> = {
    award: [
      ['first', t('places.first', { defaultValue: placeLabel.first })],
      ['runner-up', t('places.runnerUp', { defaultValue: placeLabel['runner-up'] })],
    ],
    tier: [
      ['verified', t('tiers.verified', { defaultValue: tierLabel.verified })],
      ['likely', t('tiers.likely', { defaultValue: tierLabel.likely })],
    ],
    track: [
      ['genesis', t('tracks.genesis', { defaultValue: trackLabel.genesis })],
      ['scale', t('tracks.scale', { defaultValue: trackLabel.scale })],
    ],
    activity: [
      ['contracts', t('explorer.filterFixed.contracts')],
      ['failed', t('explorer.filterFixed.failed')],
    ],
  }

  const labelled: [string, string, string?][] =
    key === 'award' || key === 'tier' || key === 'track' || key === 'activity'
      ? fixedLabels[key].map(([value, label]) => [value, label])
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

  const isFixed = key in fixedLabels
  return labelled
    .map(([value, label, hint]) => ({ value, label, hint, count: counts.get(value) ?? 0 }))
    .filter((option) => option.count > 0 || chosen.has(option.value))
    .sort((a, b) => (isFixed ? 0 : b.count - a.count || a.label.localeCompare(b.label)))
}

function Group({
  title,
  items,
  chosen,
  onToggle,
  collapsible,
  t,
}: {
  title: string
  items: Option[]
  chosen: string[]
  onToggle: (value: string) => void
  collapsible: boolean
  t: (k: string, opts?: Record<string, unknown>) => string
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
          {expanded ? t('explorer.showLess') : t('explorer.showAll', { count: items.length })}
        </button>
      )}
    </fieldset>
  )
}

export function FilterPanel({
  projects,
  integrations,
  selection,
  onToggle,
  onClear,
}: FilterPanelProps) {
  const active = selectedCount(selection)
  const { t } = useTranslation()

  const groups: { key: FilterKey; title: string; collapsible: boolean }[] = [
    { key: 'award', title: t('explorer.filterGroups.award'), collapsible: false },
    { key: 'tier', title: t('explorer.filterGroups.tier'), collapsible: false },
    { key: 'track', title: t('explorer.filterGroups.track'), collapsible: false },
    { key: 'partner', title: t('explorer.filterGroups.partner'), collapsible: true },
    { key: 'activity', title: t('explorer.filterGroups.activity'), collapsible: false },
    { key: 'language', title: t('explorer.filterGroups.language'), collapsible: true },
    { key: 'country', title: t('explorer.filterGroups.country'), collapsible: true },
  ]

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <h2 className="font-heading text-lg">{t('explorer.filters')}</h2>
        {active > 0 && (
          <Button variant="ghost" size="sm" onClick={onClear}>
            {t('explorer.clear')} {active}
          </Button>
        )}
      </div>
      {groups.map(({ key, title, collapsible }) => (
        <Group
          key={key}
          title={title}
          items={options(key, projects, integrations, selection, t)}
          chosen={selection[key]}
          onToggle={(value) => onToggle(key, value)}
          collapsible={collapsible}
          t={t}
        />
      ))}
    </div>
  )
}
