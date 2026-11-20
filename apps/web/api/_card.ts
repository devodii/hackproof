export interface Stat {
  value: string
  label: string
}

export interface Card {
  eyebrow: string
  title: string
  accent: string | null
  subtitle: string | null
  stats: Stat[]
  avatar: string | null
  meter: { lit: number; caption: string } | null
  title_for_page: string
}

const compact = new Intl.NumberFormat('en', { maximumFractionDigits: 0 })
const day = new Intl.DateTimeFormat('en', { month: 'short', day: 'numeric', timeZone: 'UTC' })
const dayYear = new Intl.DateTimeFormat('en', {
  month: 'short',
  day: 'numeric',
  year: 'numeric',
  timeZone: 'UTC',
})

const TIER = { verified: 'Verified on-chain', likely: 'Code only', possible: 'Possible' } as const
const AWARD = { first: '1st place', 'runner-up': 'Runner-up' } as const

interface Hackathon {
  slug: string
  name: string
  summary: string | null
  location: string | null
  starts_at: string
  ends_at: string
  indexed: boolean
  projects: number
  verified_projects: number
  contracts: number
  winners: number
}

async function get<T>(api: string, path: string): Promise<T | null> {
  try {
    const response = await fetch(`${api}/api${path}`)
    return response.ok ? ((await response.json()) as T) : null
  } catch {
    return null
  }
}

export function splitYear(name: string) {
  const found = /^(.*?)\s*(\d{4})$/.exec(name)
  return found ? { title: found[1], year: found[2] } : { title: name, year: null }
}

const plural = (count: number, word: string) => (count === 1 ? word : `${word}s`)

function range(start: string, end: string) {
  const [a, b] = [new Date(start), new Date(end)]
  if (a.toDateString() === b.toDateString()) return dayYear.format(a)
  const sameYear = a.getUTCFullYear() === b.getUTCFullYear()
  return `${sameYear ? day.format(a) : dayYear.format(a)} to ${dayYear.format(b)}`
}

function clip(text: string | null, length: number) {
  if (!text) return null
  const sentence = /^.+?[.!?](?=\s|$)/.exec(text)?.[0]
  if (sentence && sentence.length <= length) return sentence
  return text.length > length ? `${text.slice(0, length - 1).trimEnd()}…` : text
}

const LANDING: Card = {
  eyebrow: 'HackProof',
  title: 'Stellar hackathons,',
  accent: 'checked on-chain.',
  subtitle: 'Every project matched to the contracts, accounts and commits behind it.',
  stats: [],
  avatar: null,
  meter: null,
  title_for_page: 'HackProof: Stellar hackathons, checked on-chain',
}

async function landing(api: string): Promise<Card> {
  const all = (await get<Hackathon[]>(api, '/hackathons')) ?? []
  const indexed = all.filter((item) => item.indexed)
  const total = (key: 'projects' | 'verified_projects' | 'contracts') =>
    indexed.reduce((count, item) => count + item[key], 0)
  const sum = (key: 'projects' | 'verified_projects' | 'contracts') => compact.format(total(key))
  if (all.length === 0) return LANDING
  return {
    ...LANDING,
    meter: {
      lit: total('projects') ? total('verified_projects') / total('projects') : 0,
      caption: `${sum('verified_projects')} of ${sum('projects')} projects verified on-chain`,
    },
    stats: [
      { value: compact.format(all.length), label: 'hackathons' },
      { value: sum('projects'), label: 'projects checked' },
      { value: sum('verified_projects'), label: 'verified on-chain' },
      { value: sum('contracts'), label: 'contracts linked' },
    ],
  }
}

async function hackathon(api: string, id: string, page: string): Promise<Card> {
  const found = ((await get<Hackathon[]>(api, '/hackathons')) ?? []).find(
    (item) => item.slug === id,
  )
  if (!found) return landing(api)
  const { title, year } = splitYear(found.name)
  const wrapped = page === 'wrapped'
  return {
    eyebrow: [range(found.starts_at, found.ends_at), found.location].filter(Boolean).join('  ·  '),
    title: wrapped ? `${found.name}` : title,
    accent: wrapped ? 'Wrapped' : year,
    subtitle: clip(found.summary, 110),
    stats: found.indexed
      ? [
          { value: compact.format(found.projects), label: 'projects' },
          { value: compact.format(found.verified_projects), label: 'verified on-chain' },
          { value: compact.format(found.contracts), label: 'linked contracts' },
          ...(found.winners ? [{ value: compact.format(found.winners), label: 'winners' }] : []),
        ]
      : [],
    avatar: null,
    meter: found.indexed
      ? {
          lit: found.projects ? found.verified_projects / found.projects : 0,
          caption: `${compact.format(found.verified_projects)} of ${compact.format(found.projects)} projects verified on-chain`,
        }
      : null,
    title_for_page: `${found.name}${wrapped ? ' Wrapped' : ''} on HackProof`,
  }
}

interface ProjectDetail {
  project: {
    project_id: string
    hackathon: string
    tier: keyof typeof TIER
    contracts: number
    builders: number
    award: keyof typeof AWARD | null
    description: string | null
    owner_avatar: string | null
    language: string | null
  }
}

async function project(api: string, id: string, projectId: string): Promise<Card> {
  const [detail, all] = await Promise.all([
    get<ProjectDetail>(api, `/projects/${projectId}?hackathon=${encodeURIComponent(id)}`),
    get<Hackathon[]>(api, '/hackathons'),
  ])
  if (!detail) return hackathon(api, id, '')
  const item = detail.project
  const name = projectId.replace(/^repo:/, '')
  const event = all?.find((entry) => entry.slug === id)?.name ?? id
  return {
    eyebrow: [event, item.award ? AWARD[item.award] : null].filter(Boolean).join('  ·  '),
    title: name,
    accent: null,
    subtitle: clip(item.description, 150),
    stats: [
      { value: TIER[item.tier], label: 'evidence' },
      { value: compact.format(item.contracts), label: 'contracts' },
      ...(item.language ? [{ value: item.language, label: 'language' }] : []),
    ],
    avatar: item.owner_avatar,
    meter: null,
    title_for_page: `${name} at ${event}`,
  }
}

interface Person {
  login: string
  avatar_url: string | null
  contributions: number
  projects: { project: { hackathon: string } }[]
}

async function builder(api: string, login: string): Promise<Card> {
  const person = await get<Person>(api, `/builders/${encodeURIComponent(login)}`)
  if (!person) return landing(api)
  const events = new Set(person.projects.map((entry) => entry.project.hackathon)).size
  return {
    eyebrow: 'Builder',
    title: person.login,
    accent: null,
    subtitle: 'Everything this builder shipped at Stellar hackathons, across every event.',
    stats: [
      {
        value: compact.format(person.projects.length),
        label: plural(person.projects.length, 'project'),
      },
      { value: compact.format(events), label: events === 1 ? 'hackathon' : 'hackathons' },
      {
        value: compact.format(person.contributions),
        label: plural(person.contributions, 'commit'),
      },
    ],
    avatar: person.avatar_url,
    meter: null,
    title_for_page: `${person.login} on HackProof`,
  }
}

interface Integration {
  slug: string
  name: string
  category: string
  projects: number
}

async function integration(api: string, slug: string): Promise<Card> {
  const [list, all] = await Promise.all([
    get<Integration[]>(api, '/integrations'),
    get<Hackathon[]>(api, '/hackathons'),
  ])
  const found = (list ?? []).find((item) => item.slug === slug)
  if (!found) return landing(api)
  const total = (all ?? []).reduce((count, item) => count + (item.indexed ? item.projects : 0), 0)
  return {
    eyebrow: `Integration  ·  ${found.category}`,
    title: found.name,
    accent: null,
    subtitle: 'Which hackathon projects use it, and how, checked against the chain.',
    stats: [{ value: compact.format(found.projects), label: 'projects using it' }],
    avatar: null,
    meter: total
      ? {
          lit: Math.min(1, found.projects / total),
          caption: `${compact.format(found.projects)} of ${compact.format(total)} projects use it`,
        }
      : null,
    title_for_page: `${found.name} on HackProof`,
  }
}

export async function describe(api: string, path: string): Promise<Card> {
  const parts = path.split('/').filter(Boolean).map(decodeURIComponent)
  const [first, second, third, ...rest] = parts
  if (first === 'hackathon' && second) {
    if (third === 'project' && rest.length > 0) return project(api, second, rest.join('/'))
    return hackathon(api, second, third ?? '')
  }
  if (first === 'builder' && second) return builder(api, second)
  if (first === 'integration' && second) return integration(api, second)
  return landing(api)
}

export function descriptionOf(card: Card) {
  return (
    card.subtitle ??
    card.stats.map((stat) => `${stat.value} ${stat.label}`).join(', ') ??
    LANDING.subtitle ??
    ''
  )
}
