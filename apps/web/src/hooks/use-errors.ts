import { useQuery } from '@tanstack/react-query'

import { apiGet } from '@/lib/api'
import type { SorobanError } from '@/lib/types'

export function useErrors() {
  return useQuery({ queryKey: ['errors'], queryFn: () => apiGet<SorobanError[]>('/errors') })
}
