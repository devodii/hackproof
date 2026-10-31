import { useTranslation } from 'react-i18next'

import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { ApiError } from '@/lib/api'

export function DetailError({ error, subject }: { error: Error; subject: string }) {
  const { t } = useTranslation()
  const notFound = error instanceof ApiError && error.status === 404

  return (
    <Alert variant={notFound ? 'default' : 'destructive'}>
      <AlertTitle>
        {notFound
          ? `${t('table.none')}: ${subject}`
          : t('table.unreachableTitle', { resource: subject })}
      </AlertTitle>
      <AlertDescription>
        {notFound
          ? t('table.none')
          : t('table.unreachableDesc')}
      </AlertDescription>
    </Alert>
  )
}
