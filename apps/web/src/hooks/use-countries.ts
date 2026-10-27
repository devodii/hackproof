import { useQuery } from '@tanstack/react-query'

import { apiGet } from '@/lib/api'
import type { CountryCount } from '@/lib/types'

export function useCountries() {
  return useQuery({ queryKey: ['countries'], queryFn: () => apiGet<CountryCount[]>('/countries') })
}
