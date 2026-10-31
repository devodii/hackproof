import { useState } from 'react'
import { Link, useSearchParams } from 'react-router'
import { CheckCircle2Icon, ShieldAlertIcon } from 'lucide-react'

import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Button, buttonVariants } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { apiPost } from '@/lib/api'

interface OptOutResponse {
  status: string
  message: string
  issue_url?: string | null
}

export function OptOutPage() {
  const [searchParams] = useSearchParams()
  const initialProjectId = searchParams.get('project_id') ?? searchParams.get('projectId') ?? ''

  const [projectId, setProjectId] = useState(initialProjectId)
  const [handle, setHandle] = useState('')
  const [reason, setReason] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [result, setResult] = useState<OptOutResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!projectId.trim() || !handle.trim()) {
      setError('Please provide both a project ID and your GitHub handle.')
      return
    }

    setIsSubmitting(true)
    setError(null)

    try {
      const response = await apiPost<OptOutResponse>('/opt-out', {
        project_id: projectId.trim(),
        handle: handle.trim(),
        reason: reason.trim() || undefined,
      })
      setResult(response)
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to submit opt out request.'
      setError(msg)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="mx-auto flex max-w-xl flex-col gap-6 py-6">
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <ShieldAlertIcon className="size-5 text-muted-foreground" />
            <CardTitle>Opt Out of Index</CardTitle>
          </div>
          <CardDescription>
            Anyone can request the removal of their project or handle from the HackProof index. We
            honor opt outs within 24h.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {result ? (
            <div className="flex flex-col gap-4">
              <Alert className="border-emerald-500/30 bg-emerald-500/10 text-emerald-900 dark:text-emerald-200">
                <CheckCircle2Icon className="size-4 text-emerald-600 dark:text-emerald-400" />
                <AlertTitle>Opt out request received</AlertTitle>
                <AlertDescription>
                  {result.message} Your request for project{' '}
                  <span className="font-mono font-semibold">{projectId}</span> has been logged.
                  {result.issue_url && (
                    <div className="mt-2">
                      <a
                        href={result.issue_url}
                        target="_blank"
                        rel="noreferrer"
                        className="underline hover:text-foreground"
                      >
                        View issue on GitHub
                      </a>
                    </div>
                  )}
                </AlertDescription>
              </Alert>
              <div className="flex justify-end">
                <Link to="/" className={buttonVariants({ variant: 'outline' })}>
                  Back to Home
                </Link>
              </div>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="flex flex-col gap-4">
              {error && (
                <Alert variant="destructive">
                  <AlertTitle>Error</AlertTitle>
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}
              <div className="flex flex-col gap-2">
                <label htmlFor="projectId" className="text-sm font-medium">
                  Project ID
                </label>
                <Input
                  id="projectId"
                  placeholder="e.g. repo:owner/repo or acct:G..."
                  value={projectId}
                  onChange={(e) => setProjectId(e.target.value)}
                  required
                />
                <span className="text-xs text-muted-foreground">
                  The repository identifier or account address listed in HackProof.
                </span>
              </div>

              <div className="flex flex-col gap-2">
                <label htmlFor="handle" className="text-sm font-medium">
                  GitHub Handle
                </label>
                <Input
                  id="handle"
                  placeholder="e.g. octocat"
                  value={handle}
                  onChange={(e) => setHandle(e.target.value)}
                  required
                />
                <span className="text-xs text-muted-foreground">
                  Your GitHub handle to verify project ownership or attribution.
                </span>
              </div>

              <div className="flex flex-col gap-2">
                <label htmlFor="reason" className="text-sm font-medium">
                  Reason (Optional)
                </label>
                <Textarea
                  id="reason"
                  placeholder="Optional note on why you wish to be removed..."
                  value={reason}
                  onChange={(e) => setReason(e.target.value)}
                  rows={3}
                />
              </div>

              <div className="rounded-lg border bg-muted/40 p-3 text-xs text-muted-foreground">
                We honor opt outs within 24h. Submitting creates a tracked removal request in our
                repository.
              </div>

              <div className="flex justify-end gap-3 pt-2">
                <Link to="/" className={buttonVariants({ variant: 'outline' })}>
                  Cancel
                </Link>
                <Button type="submit" disabled={isSubmitting}>
                  {isSubmitting ? 'Submitting...' : 'Submit Opt Out Request'}
                </Button>
              </div>
            </form>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
