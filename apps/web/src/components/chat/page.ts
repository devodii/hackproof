import { FILTER_KEYS, readSelection } from '@/components/explorer/filters'

export type PageKind = 'home' | 'project' | 'builder' | 'filter'

export interface PageContext {
  kind: PageKind
  id?: string
  filters?: Record<string, string[]>
}

export function currentPage(): PageContext {
  const { search } = window.location
  const pathname = window.location.pathname.replace(/^\/hackathon\/[^/]+/, '') || '/'
  if (pathname.startsWith('/project/')) {
    return { kind: 'project', id: decodeURIComponent(pathname.slice('/project/'.length)) }
  }
  if (pathname.startsWith('/builder/')) {
    return { kind: 'builder', id: decodeURIComponent(pathname.slice('/builder/'.length)) }
  }
  const filters = activeFilters(new URLSearchParams(search))
  if (pathname === '/' && Object.keys(filters).length > 0) return { kind: 'filter', filters }
  return { kind: 'home' }
}

function activeFilters(params: URLSearchParams) {
  const selection = readSelection(params)
  return Object.fromEntries(
    FILTER_KEYS.filter((key) => selection[key].length > 0).map((key) => [key, selection[key]]),
  )
}

const SUGGESTIONS: Partial<Record<PageKind, string[]>> = {
  home: [
    'Who won, and what did they build?',
    'Did the teams that deployed the most contracts win?',
    'When was the busiest hour of the hack?',
    'Which Stellar tools did most teams build on?',
    'What can I learn from the winners to prepare for 2027?',
  ],
  project: [
    'Summarize this project',
    'What is it built with?',
    'How does it compare to the winners?',
    'How do we know it was really built on-chain?',
  ],
  builder: [
    'What has this builder shipped?',
    'Which contracts did they deploy?',
    'Did any of their transactions fail?',
  ],
}

export function suggestionsFor(kind: PageKind) {
  return SUGGESTIONS[kind] ?? []
}
