import { useQuery } from '@tanstack/react-query'

import { apiGet } from '@/lib/api'
import type { IntegrationDetail, Reading } from '@/lib/types'

const LIVE_REFRESH_MS = 30_000

export function useIntegration(slug: string) {
  return useQuery({
    queryKey: ['integration', slug],
    queryFn: () => apiGet<IntegrationDetail>(`/integrations/${slug}`),
  })
}

export function useIntegrationLive(slug: string, enabled: boolean) {
  return useQuery({
    queryKey: ['integration', slug, 'live'],
    queryFn: () => apiGet<Reading[]>(`/integrations/${slug}/live`),
    enabled,
    refetchInterval: LIVE_REFRESH_MS,
  })
}
