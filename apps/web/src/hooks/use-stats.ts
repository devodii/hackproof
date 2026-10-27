import { useQuery } from '@tanstack/react-query'

import { apiGet } from '@/lib/api'
import type { Stats } from '@/lib/types'

export function useStats() {
  return useQuery({ queryKey: ['stats'], queryFn: () => apiGet<Stats>('/stats') })
}
