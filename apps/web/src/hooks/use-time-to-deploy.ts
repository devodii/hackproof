import { useQuery } from '@tanstack/react-query'

import { apiGet } from '@/lib/api'
import type { TimeToDeployData } from '@/lib/types'

export function useTimeToDeploy() {
  return useQuery({
    queryKey: ['time-to-deploy'],
    queryFn: () => apiGet<TimeToDeployData>('/time-to-deploy'),
  })
}
