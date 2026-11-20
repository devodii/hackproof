import { QueryClientProvider } from '@tanstack/react-query'
import * as React from 'react'
import { Outlet, useParams } from 'react-router'

import { HackathonContext } from '@/hooks/use-hackathon'
import { useHackathons } from '@/hooks/use-hackathons'
import { selectHackathon } from '@/lib/hackathon'
import { createQueryClient } from '@/lib/query-client'
import { Frame } from '@/components/layout/frame'
import { HackathonPendingPage } from '@/pages/hackathon-pending'
import { NotFoundPage } from '@/pages/not-found'

export function HackathonScope() {
  const { id = '' } = useParams()
  const { data, isPending } = useHackathons()
  const hackathon = data?.find((item) => item.slug === id) ?? null
  const client = React.useMemo(createQueryClient, [id])

  if (isPending) return null
  if (hackathon === null) return <NotFoundPage />
  selectHackathon(id)

  return (
    <HackathonContext.Provider value={hackathon}>
      <QueryClientProvider client={client}>
        {hackathon.indexed ? (
          <Outlet />
        ) : (
          <Frame>
            <HackathonPendingPage />
          </Frame>
        )}
      </QueryClientProvider>
    </HackathonContext.Provider>
  )
}
