import { CheckIcon, CopyIcon } from 'lucide-react'
import { useState } from 'react'
import { Link, useParams } from 'react-router'

import { DetailError, DetailSkeleton } from '@/components/query-state'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { useProof } from '@/hooks/use-proof'
import { formatDateTime, formatNumber } from '@/lib/format'

export function ProofPage() {
  const address = useParams().address ?? ''
  const { data, isPending, error } = useProof(address)
  const [copied, setCopied] = useState(false)

  if (isPending) return <DetailSkeleton />
  if (error) return <DetailError error={error} subject="proof" />

  const copyLink = async () => {
    await navigator.clipboard.writeText(window.location.href)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const counts = [
    { label: 'Projects', value: data.projects },
    { label: 'Contracts', value: data.contracts },
    { label: 'Wasm uploads', value: data.wasm_uploads },
    { label: 'Failed txs', value: data.failed_txs },
  ]

  return (
    <Card className="mx-auto w-full max-w-2xl">
      <CardHeader>
        <span className="font-mono text-xs text-muted-foreground">proof #{data.proof_id}</span>
        <CardTitle className="text-2xl">Proof of hack</CardTitle>
        <Link
          to={`/builder/${data.address}`}
          className="font-mono text-sm break-all text-muted-foreground hover:underline"
        >
          {data.address}
        </Link>
      </CardHeader>
      <CardContent className="flex flex-col gap-6">
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
          {counts.map(({ label, value }) => (
            <div key={label} className="flex flex-col">
              <span className="text-xs text-muted-foreground">{label}</span>
              <span className="text-2xl font-semibold tabular-nums">{formatNumber(value)}</span>
            </div>
          ))}
        </div>
        <dl className="grid gap-1 text-sm text-muted-foreground">
          <div>
            First activity{' '}
            <span className="text-foreground">{formatDateTime(data.first_activity)}</span>
          </div>
          <div>
            Last activity{' '}
            <span className="text-foreground">{formatDateTime(data.last_activity)}</span>
          </div>
          <div>
            Claimed <span className="text-foreground">{formatDateTime(data.claimed_at)}</span>
          </div>
        </dl>
        <Button variant="outline" onClick={copyLink} className="w-fit">
          {copied ? <CheckIcon /> : <CopyIcon />}
          {copied ? 'Copied' : 'Copy link'}
        </Button>
      </CardContent>
    </Card>
  )
}
