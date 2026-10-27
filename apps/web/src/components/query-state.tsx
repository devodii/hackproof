import { ApiError } from '@/lib/api'

import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Skeleton } from '@/components/ui/skeleton'

export function DetailSkeleton() {
  return (
    <div className="flex flex-col gap-4">
      <Skeleton className="h-10 w-72" />
      <Skeleton className="h-5 w-96 max-w-full" />
      <Skeleton className="h-64 w-full" />
    </div>
  )
}

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
