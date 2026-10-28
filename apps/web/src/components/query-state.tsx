import { ApiError } from '@/lib/api'

import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'

export function DetailError({ error, subject }: { error: Error; subject: string }) {
  const notFound = error instanceof ApiError && error.status === 404
  return (
    <Alert variant={notFound ? 'default' : 'destructive'}>
      <AlertTitle>{notFound ? `No ${subject} found` : `Could not load ${subject}`}</AlertTitle>
      <AlertDescription>
        {notFound
          ? 'Nothing on testnet matches this inside the hack window.'
          : 'The API is unreachable. Try again in a moment.'}
      </AlertDescription>
    </Alert>
  )
}
