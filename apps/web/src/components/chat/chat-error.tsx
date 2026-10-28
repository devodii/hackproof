import { useEffect, useState } from 'react'

import { RateLimitError, UnavailableError } from '@/components/chat/transport'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'

function wait(seconds: number) {
  return seconds >= 90 ? `${Math.ceil(seconds / 60)} minutes` : `${seconds} seconds`
}

function useCountdown(seconds: number) {
  const [remaining, setRemaining] = useState(seconds)

  useEffect(() => {
    if (remaining <= 0) return
    const timer = setTimeout(() => setRemaining((value) => value - 1), 1000)
    return () => clearTimeout(timer)
  }, [remaining])

  return remaining
}

function RateLimited({ error, onRetry }: { error: RateLimitError; onRetry: () => void }) {
  const remaining = useCountdown(error.retryAfter)

  return (
    <Alert>
      <AlertTitle>You are sending messages too fast</AlertTitle>
      <AlertDescription>
        <p>
          Chat is limited to 10 messages a minute and 50 an hour.{' '}
          {remaining > 0
            ? `Try again in ${wait(remaining)}.`
            : `The ${error.window} limit has reset.`}
        </p>
        {remaining === 0 && (
          <Button size="sm" variant="outline" className="mt-2" onClick={onRetry}>
            Send again
          </Button>
        )}
      </AlertDescription>
    </Alert>
  )
}

export function ChatError({ error, onRetry }: { error: Error; onRetry: () => void }) {
  if (error instanceof RateLimitError) return <RateLimited error={error} onRetry={onRetry} />

  const unavailable = error instanceof UnavailableError
  return (
    <Alert variant="destructive">
      <AlertTitle>{unavailable ? 'Chat is not available' : 'Something went wrong'}</AlertTitle>
      <AlertDescription>
        <p>
          {unavailable
            ? 'The assistant is not configured on this server yet.'
            : 'The reply could not be completed.'}
        </p>
        {!unavailable && (
          <Button size="sm" variant="outline" className="mt-2" onClick={onRetry}>
            Try again
          </Button>
        )}
      </AlertDescription>
    </Alert>
  )
}
