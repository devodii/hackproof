import * as React from 'react'
import { Link as RouterLink, useNavigate } from 'react-router'

import { HackathonContext } from '@/hooks/use-hackathon'
import { hackathonPath } from '@/lib/hackathon'

function scoped(slug: string | undefined, to: string) {
  return slug !== undefined && to.startsWith('/') ? hackathonPath(slug, to) : to
}

export function Link({ to, ...props }: React.ComponentProps<typeof RouterLink>) {
  const hackathon = React.useContext(HackathonContext)
  return <RouterLink to={typeof to === 'string' ? scoped(hackathon?.slug, to) : to} {...props} />
}

export function useHackathonNavigate() {
  const hackathon = React.useContext(HackathonContext)
  const navigate = useNavigate()
  return React.useCallback(
    (to: string) => navigate(scoped(hackathon?.slug, to)),
    [hackathon?.slug, navigate],
  )
}
