import * as React from 'react'

import { hackathonPath } from '@/lib/hackathon'
import type { HackathonSummary } from '@/lib/types'

export const HackathonContext = React.createContext<HackathonSummary | null>(null)

export function useHackathon() {
  const hackathon = React.useContext(HackathonContext)
  if (hackathon === null) throw new Error('useHackathon needs a hackathon page')
  return hackathon
}

export function useHackathonPath() {
  const { slug } = useHackathon()
  return React.useCallback((path = '') => hackathonPath(slug, path), [slug])
}
