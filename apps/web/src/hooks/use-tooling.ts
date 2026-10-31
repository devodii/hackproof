import { useQuery } from '@tanstack/react-query'

import { apiGet } from '@/lib/api'
import type { ToolingStats } from '@/lib/types'

export function useTooling() {
  return useQuery({ queryKey: ['tooling'], queryFn: () => apiGet<ToolingStats>('/tooling') })
}
