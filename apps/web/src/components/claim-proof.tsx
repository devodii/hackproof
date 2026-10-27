import { WalletIcon } from 'lucide-react'
import { useNavigate } from 'react-router'
import { toast } from 'sonner'

import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { useClaimProof } from '@/hooks/use-claim-proof'

export function ClaimProof() {
  const navigate = useNavigate()
  const { mutate, isPending } = useClaimProof()

  const claim = () =>
    mutate(undefined, {
      onSuccess: (proof) => navigate(`/proof/${proof.address}`),
      onError: (error) => toast.error(error.message || 'Could not claim the proof'),
    })

  return (
    <Card>
      <CardHeader>
        <CardTitle>Claim your proof of hack</CardTitle>
        <CardDescription>
          If you deployed during the hack, connect the key you deployed from and sign once. Nothing
          is sent on chain and no funds move.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Button onClick={claim} disabled={isPending}>
          <WalletIcon />
          {isPending ? 'Waiting for wallet' : 'Connect wallet'}
        </Button>
      </CardContent>
    </Card>
  )
}
