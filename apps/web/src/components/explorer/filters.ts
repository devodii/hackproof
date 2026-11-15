import type { Project } from '@/lib/types'

export const FILTER_KEYS = [
  'award',
  'tier',
  'track',
  'partner',
  'tool',
  'agent',
  'activity',
  'language',
  'country',
] as const
export type FilterKey = (typeof FILTER_KEYS)[number]
export type Selection = Record<FilterKey, string[]>

const VALUES: Record<FilterKey, (project: Project) => string[]> = {
  award: (project) => (project.award ? [project.award] : []),
  tier: (project) => [project.tier],
  track: (project) => (project.track ? [project.track] : []),
  partner: (project) => project.integrations ?? [],
  tool: (project) => project.tools ?? [],
  agent: (project) => project.agents ?? [],
  activity: (project) => [
    ...(project.contracts > 0 ? ['contracts'] : []),
    ...(project.failed_txs > 0 ? ['failed'] : []),
  ],
  language: (project) => (project.language ? [project.language] : []),
  country: (project) => (project.country ? [project.country] : []),
}

export function readSelection(params: URLSearchParams): Selection {
  return Object.fromEntries(
    FILTER_KEYS.map((key) => [
      key,
      params
        .getAll(key)
        .flatMap((value) => value.split(','))
        .map((value) => (key === 'tool' ? value.replaceAll('_', '-') : value))
        .filter(Boolean),
    ]),
  ) as Selection
}

export function matches(project: Project, selection: Selection, skip?: FilterKey) {
  return FILTER_KEYS.every(
    (key) =>
      key === skip ||
      selection[key].length === 0 ||
      VALUES[key](project).some((value) => selection[key].includes(value)),
  )
}

export function countValues(projects: Project[], selection: Selection, key: FilterKey) {
  const counts = new Map<string, number>()
  for (const project of projects) {
    if (!matches(project, selection, key)) continue
    for (const value of VALUES[key](project)) counts.set(value, (counts.get(value) ?? 0) + 1)
  }
  return counts
}

export function selectedCount(selection: Selection) {
  return FILTER_KEYS.reduce((total, key) => total + selection[key].length, 0)
}
