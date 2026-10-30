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
    'Who won HackMeridian, and what did they build?',
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
  return SUGGESTIONS[kind]
}
