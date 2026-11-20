import { useQuery } from '@tanstack/react-query'

import { apiGet } from '@/lib/api'
import type { Account } from '@/lib/types'

export function useAccount(address: string) {
  return useQuery({
    queryKey: ['account', address],
    queryFn: () => apiGet<Account>(`/accounts/${address}`),
  })
}
