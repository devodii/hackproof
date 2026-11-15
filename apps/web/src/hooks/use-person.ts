import { useQuery } from '@tanstack/react-query'

import { apiGet } from '@/lib/api'
import type { Person } from '@/lib/types'

export function usePerson(login: string) {
  return useQuery({
    queryKey: ['person', login],
    queryFn: () => apiGet<Person>(`/contributors/${encodeURIComponent(login)}`),
  })
}
