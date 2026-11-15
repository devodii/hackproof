import { useLocation } from 'react-router'

import { currentPage, suggestionsFor } from '@/components/chat/page'
import { filterQuestions } from '@/components/explorer/filter-options'
import { useSelectedGroups } from '@/components/explorer/use-selected-groups'

export function useSuggestions() {
  const { pathname } = useLocation()
  const { groups } = useSelectedGroups()

  if (pathname === '/' && groups.length > 0) return filterQuestions(groups)
  return suggestionsFor(currentPage().kind)
}
