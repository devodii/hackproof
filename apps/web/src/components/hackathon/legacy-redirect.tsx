import { Navigate, useLocation } from 'react-router'

import { useHackathons } from '@/hooks/use-hackathons'
import { hackathonPath } from '@/lib/hackathon'

export function LegacyRedirect() {
  const { pathname, search } = useLocation()
  const { data, isPending } = useHackathons()
  const first = data
    ?.filter((hackathon) => hackathon.indexed)
    .sort((a, b) => a.starts_at.localeCompare(b.starts_at))[0]

  if (isPending) return null
  if (first === undefined) return <Navigate to="/" replace />
  return (
    <Navigate
      to={`${hackathonPath(first.slug, pathname === '/' ? '' : pathname)}${search}`}
      replace
    />
  )
}
