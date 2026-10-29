import { useInfiniteQuery } from '@tanstack/react-query'

import { PAGE_SIZE } from '@/hooks/use-paged-list'
import { apiGet } from '@/lib/api'
import type { Page } from '@/lib/types'

export function useInfiniteList<T>(resource: string, search: string) {
  return useInfiniteQuery({
    queryKey: [resource, 'infinite', search],
    initialPageParam: 0,
    queryFn: ({ pageParam }) => {
      const params = new URLSearchParams({ limit: String(PAGE_SIZE), offset: String(pageParam) })
      if (search) params.set('q', search)
      return apiGet<Page<T>>(`/${resource}?${params}`)
    },
    getNextPageParam: (last, pages) => {
      const loaded = pages.length * PAGE_SIZE
      return loaded < last.total ? loaded : undefined
    },
  })
}
