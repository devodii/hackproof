import type { Project, TimelinePoint } from '@/lib/types'

export const EASE_OUT = [0.22, 1, 0.36, 1] as const
export const EASE_SPRING = [0.34, 1.56, 0.64, 1] as const
export const EASE_SETTLE = [0.16, 1, 0.3, 1] as const

export type LensKind = 'tier' | 'agent' | 'tool' | 'integration' | 'language'

export interface Lens {
  kind: LensKind
  value: string
}

const KINDS: readonly LensKind[] = ['tier', 'agent', 'tool', 'integration', 'language']

const matchers: Record<LensKind, (project: Project, value: string) => boolean> = {
  tier: (project, value) => project.tier === value,
  agent: (project, value) => project.agents.includes(value),
  tool: (project, value) => project.tools.includes(value),
  integration: (project, value) => project.integrations.includes(value),
  language: (project, value) => project.language === value,
}

const EXPLORER_FILTER: Record<LensKind, string> = {
  tier: 'tier',
  agent: 'agent',
  tool: 'tool',
  integration: 'partner',
  language: 'language',
}

export function explorerPath(lens: Lens) {
  return `/?${EXPLORER_FILTER[lens.kind]}=${encodeURIComponent(lens.value)}`
}

export function parseLens(raw: string | null): Lens | null {
  const [kind, ...rest] = (raw ?? '').split(':')
  const value = rest.join(':')
  return KINDS.includes(kind as LensKind) && value ? { kind: kind as LensKind, value } : null
}

export function isSameLens(first: Lens | null, second: Lens) {
  return first?.kind === second.kind && first.value === second.value
}

export function matchesLens(project: Project, lens: Lens) {
  return matchers[lens.kind](project, lens.value)
}

export function percent(value: number, total: number) {
  return Math.round((value / total) * 100)
}

const RUSH_HOURS = 2

export function timelineHighlights(timeline: TimelinePoint[]) {
  const peak = timeline.reduce((best, point) => (point.contracts > best.contracts ? point : best))
  const rush = timeline.slice(-RUSH_HOURS)
  return { peak, rush, rushTotal: rush.reduce((sum, point) => sum + point.contracts, 0) }
}
