import { keepPreviousData, useQuery } from '@tanstack/react-query'

import { apiGet } from '@/lib/api'
import type { Page } from '@/lib/types'

export const PAGE_SIZE = 25

export function usePagedList<T>(
  resource: string,
  search: string,
  page: number,
  tiers: readonly string[] = [],
) {
  const params = new URLSearchParams({
    limit: String(PAGE_SIZE),
    offset: String(page * PAGE_SIZE),
  })
  if (search) params.set('q', search)
  tiers.forEach((tier) => params.append('tier', tier))

  return useQuery({
    queryKey: [resource, search, page, tiers],
    queryFn: () => apiGet<Page<T>>(`/${resource}?${params}`),
    placeholderData: keepPreviousData,
  })
}
