import { countryName, flagEmoji, placeLabel, tierLabel, trackLabel } from '@/lib/format'
import type { AiAgent, EcosystemTool, Integration, Project } from '@/lib/types'

import { countValues, type FilterKey, type Selection } from './filters'

export interface Option {
  value: string
  label: string
  count: number
  hint?: string
}

const FIXED: Record<'award' | 'tier' | 'track' | 'activity', [string, string][]> = {
  award: [
    ['first', placeLabel.first],
    ['runner-up', placeLabel['runner-up']],
  ],
  tier: [
    ['verified', tierLabel.verified],
    ['likely', tierLabel.likely],
  ],
  track: [
    ['genesis', trackLabel.genesis],
    ['scale', trackLabel.scale],
  ],
  activity: [
    ['contracts', 'Deployed contracts'],
    ['failed', 'Failed transactions'],
  ],
}

export function options(
  key: FilterKey,
  projects: Project[],
  integrations: Integration[],
  tools: EcosystemTool[],
  agents: AiAgent[],
  selection: Selection,
): Option[] {
  const counts = countValues(projects, selection, key)
  const chosen = new Set(selection[key])
  const labelled: [string, string, string?][] =
    key === 'award' || key === 'tier' || key === 'track' || key === 'activity'
      ? FIXED[key].map(([value, label]) => [value, label])
      : key === 'partner'
        ? integrations.map((item) => [item.slug, item.name, item.category])
        : key === 'tool'
          ? tools.map((item) => [item.slug, item.name])
          : key === 'agent'
            ? agents.map((item) => [item.slug, item.name])
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
    .sort((a, b) => (key in FIXED ? 0 : b.count - a.count || a.label.localeCompare(b.label)))
}

export const GROUPS: { key: FilterKey; title: string; collapsible: boolean }[] = [
  { key: 'award', title: 'Awards', collapsible: false },
  { key: 'tier', title: 'Evidence', collapsible: false },
  { key: 'track', title: 'Track', collapsible: false },
  { key: 'partner', title: 'Integrations', collapsible: true },
  { key: 'tool', title: 'Ecosystem tooling', collapsible: false },
  { key: 'agent', title: 'AI coding agents', collapsible: false },
  { key: 'activity', title: 'On-chain activity', collapsible: false },
  { key: 'language', title: 'Language', collapsible: true },
  { key: 'country', title: 'Country', collapsible: true },
]
