import { useQuery } from '@tanstack/react-query'

import { apiGet } from '@/lib/api'
import type { Builder } from '@/lib/types'

export function useBuilder(address: string) {
  return useQuery({
    queryKey: ['builder', address],
    queryFn: () => apiGet<Builder>(`/builders/${address}`),
  })
}
