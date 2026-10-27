import { useMutation, useQueryClient } from '@tanstack/react-query'

import { apiPost } from '@/lib/api'
import type { Challenge, Proof } from '@/lib/types'
import { connectWallet, signMessage } from '@/lib/wallet'

async function claimProof() {
  const address = await connectWallet()
  const { message } = await apiPost<Challenge>('/proof/challenge', { address })
  const signature = await signMessage(message, address)
  return apiPost<Proof>('/proof/claim', { address, message, signature })
}

export function useClaimProof() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: claimProof,
    onSuccess: (proof) => queryClient.setQueryData(['proof', proof.address], proof),
  })
}
