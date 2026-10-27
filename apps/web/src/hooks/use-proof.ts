import { useQuery } from '@tanstack/react-query'

import { apiGet } from '@/lib/api'
import type { Proof } from '@/lib/types'

export function useProof(address: string) {
  return useQuery({
    queryKey: ['proof', address],
    queryFn: () => apiGet<Proof>(`/proof/${address}`),
  })
}
