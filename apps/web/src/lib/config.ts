const CONTACT_EMAIL = 'emmanuelodii80@gmail.com'
export const REPO_URL = 'https://github.com/devodii/hackproof'

export function optOutHref(projectId: string) {
  const subject = encodeURIComponent(`hackproof opt out: ${projectId}`)
  return `mailto:${CONTACT_EMAIL}?subject=${subject}`
}
