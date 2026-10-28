export type PageKind = 'home' | 'project' | 'builder'

export interface PageContext {
  kind: PageKind
  id?: string
}

export function currentPage(): PageContext {
  const { pathname } = window.location
  if (pathname.startsWith('/project/')) {
    return { kind: 'project', id: decodeURIComponent(pathname.slice('/project/'.length)) }
  }
  if (pathname.startsWith('/builder/')) {
    return { kind: 'builder', id: decodeURIComponent(pathname.slice('/builder/'.length)) }
  }
  return { kind: 'home' }
}

const SUGGESTIONS: Record<PageKind, string[]> = {
  home: [
    'Which projects deployed the most contracts?',
    'How many projects are verified on-chain?',
    'When was the busiest hour of the hack?',
    'Which countries had the most builders?',
  ],
  project: [
    'Summarize this project',
    'Why is it linked to the chain?',
    'Who built it?',
    'How active was it during the hack?',
  ],
  builder: [
    'What has this builder shipped?',
    'Which contracts did they deploy?',
    'Did any of their transactions fail?',
  ],
}

export function suggestionsFor(kind: PageKind) {
  return SUGGESTIONS[kind]
}
