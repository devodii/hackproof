import { useQuery } from '@tanstack/react-query'

import { apiGet } from '@/lib/api'
import type { Person } from '@/lib/types'

export function useBuilder(login: string) {
  return useQuery({
    queryKey: ['builder', login],
    queryFn: () => apiGet<Person>(`/builders/${encodeURIComponent(login)}`),
  })
}
