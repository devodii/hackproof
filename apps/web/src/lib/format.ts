const dateTime = new Intl.DateTimeFormat('en', {
  dateStyle: 'medium',
  timeStyle: 'short',
  timeZone: 'UTC',
})

const compact = new Intl.NumberFormat('en', { notation: 'compact', maximumFractionDigits: 1 })

export function formatDateTime(iso: string) {
  return `${dateTime.format(new Date(iso))} UTC`
}

const regionNames = new Intl.DisplayNames(['en'], { type: 'region' })

export function countryName(countryCode: string) {
  return regionNames.of(countryCode) ?? countryCode
}

const hourOfDay = new Intl.DateTimeFormat('en', {
  hour: '2-digit',
  hourCycle: 'h23',
  timeZone: 'UTC',
})

export function formatHour(iso: string) {
  return `${hourOfDay.format(new Date(iso))}:00`
}

export function formatNumber(value: number) {
  return value.toLocaleString('en')
}

export function formatBytes(bytes: number) {
  return `${compact.format(bytes)}B`
}

export function shortId(value: string, head = 6, tail = 4) {
  return value.length > head + tail + 1 ? `${value.slice(0, head)}…${value.slice(-tail)}` : value
}

export function flagEmoji(countryCode: string) {
  return String.fromCodePoint(
    ...[...countryCode.toUpperCase()].map((c) => 0x1f1a5 + c.charCodeAt(0)),
  )
}

export function projectName(projectId: string) {
  return projectId.startsWith('repo:')
    ? projectId.slice('repo:'.length)
    : shortId(projectId.slice('acct:'.length), 6, 6)
}

export function isWithin(iso: string | null, window: { start: string; end: string } | undefined) {
  if (!iso || !window) return false
  const time = new Date(iso).getTime()
  return time >= new Date(window.start).getTime() && time <= new Date(window.end).getTime()
}

export const tierLabel = {
  verified: 'Verified on-chain',
  likely: 'Code only',
  possible: 'Possible',
  unattributed: 'No repo',
} as const

export const placeLabel = {
  first: '1st place',
  'runner-up': 'Runner-up',
} as const

export const STRICT_TIERS = ['verified', 'likely'] as const

export const footprintLabel = {
  contracts: 'Contracts',
  classic: 'Classic ops only',
  github: 'GitHub only',
} as const

export function formatLastActivity(iso: string | null) {
  return iso ? formatDateTime(iso) : 'none'
}
