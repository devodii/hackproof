let selected: string | null = null

export function selectHackathon(id: string | null) {
  selected = id
}

export function selectedHackathon() {
  return selected
}

const GLOBAL = ['/builder/', '/hackathon/']

export function isGlobalPath(path: string) {
  return GLOBAL.some((prefix) => path.startsWith(prefix))
}

export function hackathonPath(id: string, path = '') {
  return `/hackathon/${id}${path}`
}

export function withHackathon(path: string) {
  if (selected === null) return path
  return `${path}${path.includes('?') ? '&' : '?'}hackathon=${encodeURIComponent(selected)}`
}
