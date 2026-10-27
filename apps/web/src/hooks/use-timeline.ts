import { useQuery } from '@tanstack/react-query'

import { apiGet } from '@/lib/api'
import type { TimelinePoint } from '@/lib/types'

export function useTimeline() {
  return useQuery({ queryKey: ['timeline'], queryFn: () => apiGet<TimelinePoint[]>('/timeline') })
}
