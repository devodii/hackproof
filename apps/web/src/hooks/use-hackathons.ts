import { useQuery } from '@tanstack/react-query'

import { apiGet } from '@/lib/api'
import type { HackathonSummary } from '@/lib/types'

export function useHackathons() {
  return useQuery({
    queryKey: ['hackathons'],
    queryFn: () => apiGet<HackathonSummary[]>('/hackathons'),
  })
}
