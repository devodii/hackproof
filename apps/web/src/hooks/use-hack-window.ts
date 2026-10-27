import { useQuery } from '@tanstack/react-query'

import { apiGet } from '@/lib/api'
import type { HackWindow } from '@/lib/types'

export function useHackWindow() {
  return useQuery({ queryKey: ['window'], queryFn: () => apiGet<HackWindow>('/window') })
}
