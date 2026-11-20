import type { HackathonSummary } from '@/lib/types'

export type StatusFilter = 'all' | HackathonSummary['status']
export type Sort = 'newest' | 'oldest' | 'projects'

export interface HackathonFilters {
  q: string
  status: StatusFilter
  year: string
  indexedOnly: boolean
  sort: Sort
}

export const STATUS_FILTERS: { value: StatusFilter; label: string }[] = [
  { value: 'all', label: 'All' },
  { value: 'live', label: 'Live' },
  { value: 'upcoming', label: 'Upcoming' },
  { value: 'past', label: 'Past' },
]

export const SORTS: { value: Sort; label: string }[] = [
  { value: 'newest', label: 'Newest first' },
  { value: 'oldest', label: 'Oldest first' },
  { value: 'projects', label: 'Most projects' },
]

export const DEFAULT_FILTERS: HackathonFilters = {
  q: '',
  status: 'all',
  year: '',
  indexedOnly: false,
  sort: 'newest',
}

export function readFilters(params: URLSearchParams): HackathonFilters {
  const status = params.get('status')
  const sort = params.get('sort')
  return {
    q: params.get('q') ?? '',
    status: STATUS_FILTERS.find((item) => item.value === status)?.value ?? 'all',
    year: params.get('year') ?? '',
    indexedOnly: params.get('indexed') === '1',
    sort: SORTS.find((item) => item.value === sort)?.value ?? 'newest',
  }
}

export function writeFilters(filters: HackathonFilters) {
  const params = new URLSearchParams()
  if (filters.q) params.set('q', filters.q)
  if (filters.status !== 'all') params.set('status', filters.status)
  if (filters.year) params.set('year', filters.year)
  if (filters.indexedOnly) params.set('indexed', '1')
  if (filters.sort !== 'newest') params.set('sort', filters.sort)
  return params
}

export function yearOf(hackathon: HackathonSummary) {
  return String(new Date(hackathon.starts_at).getUTCFullYear())
}

export function yearsOf(hackathons: HackathonSummary[]) {
  return [...new Set(hackathons.map(yearOf))].sort().reverse()
}

export function filterHackathons(hackathons: HackathonSummary[], filters: HackathonFilters) {
  const needle = filters.q.trim().toLowerCase()
  const found = hackathons.filter(
    (item) =>
      (filters.status === 'all' || item.status === filters.status) &&
      (filters.year === '' || yearOf(item) === filters.year) &&
      (!filters.indexedOnly || item.indexed) &&
      (needle === '' ||
        [item.name, item.slug, item.location, item.summary].some((field) =>
          field?.toLowerCase().includes(needle),
        )),
  )
  const order: Record<Sort, (a: HackathonSummary, b: HackathonSummary) => number> = {
    newest: (a, b) => b.starts_at.localeCompare(a.starts_at),
    oldest: (a, b) => a.starts_at.localeCompare(b.starts_at),
    projects: (a, b) => b.projects - a.projects || b.starts_at.localeCompare(a.starts_at),
  }
  return found.sort(order[filters.sort])
}
