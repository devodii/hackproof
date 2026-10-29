import { useFeatureFlagVariantKey } from 'posthog-js/react'

export type PaginationMode = 'scroll' | 'click'

export function usePaginationMode(): PaginationMode {
  return useFeatureFlagVariantKey('pagination') === 'click' ? 'click' : 'scroll'
}
