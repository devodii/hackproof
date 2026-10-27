import { useQuery } from '@tanstack/react-query'

import { apiGet, type HackWindow } from '@/lib/api'

export function useHackWindow() {
  return useQuery({ queryKey: ['window'], queryFn: () => apiGet<HackWindow>('/window') })
}
