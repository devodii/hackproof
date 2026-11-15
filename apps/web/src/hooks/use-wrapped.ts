import { useQuery } from '@tanstack/react-query'

import { apiGet } from '@/lib/api'
import type { Wrapped } from '@/lib/types'

export function useWrapped() {
  return useQuery({ queryKey: ['wrapped'], queryFn: () => apiGet<Wrapped>('/wrapped') })
}
