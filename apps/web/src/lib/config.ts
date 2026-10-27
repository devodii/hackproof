const CONTACT_EMAIL = import.meta.env.VITE_CONTACT_EMAIL ?? 'hello@hackproof.dev'
export const REPO_URL = 'https://github.com/devodii/hackproof'

export function optOutHref(projectId: string) {
  const subject = encodeURIComponent(`hackproof opt out: ${projectId}`)
  return `mailto:${CONTACT_EMAIL}?subject=${subject}`
}
