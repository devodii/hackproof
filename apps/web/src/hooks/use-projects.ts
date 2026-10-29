import { useQuery } from '@tanstack/react-query'

import { apiGet } from '@/lib/api'
import { STRICT_TIERS } from '@/lib/format'
import type { Integration, Page, Project } from '@/lib/types'

const EVERYTHING = 200

export function useProjects() {
  const params = new URLSearchParams({ limit: String(EVERYTHING) })
  STRICT_TIERS.forEach((tier) => params.append('tier', tier))

  return useQuery({
    queryKey: ['projects', 'all'],
    queryFn: async () => (await apiGet<Page<Project>>(`/projects?${params}`)).items,
  })
}

export function useIntegrations() {
  return useQuery({
    queryKey: ['integrations'],
    queryFn: () => apiGet<Integration[]>('/integrations'),
    staleTime: Infinity,
  })
}
