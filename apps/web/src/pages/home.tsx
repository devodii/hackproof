import { useTranslation } from 'react-i18next'

import { suggestionsFor } from '@/components/chat/page'
import { useChatPanel } from '@/components/chat/use-chat-panel'
import { Explorer } from '@/components/explorer/explorer'
import { Overview } from '@/components/overview'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { useHackWindow } from '@/hooks/use-hack-window'
import { formatDateTime } from '@/lib/format'

export function HomePage() {
  const { data } = useHackWindow()
  const { startChat } = useChatPanel()
  const { t } = useTranslation()

  return (
    <div className="flex flex-col gap-10">
      <section className="flex flex-col items-start gap-5">
        <h1 className="max-w-4xl text-5xl leading-[1.02] text-balance sm:text-7xl">
          {t('home.heroTitle')}
        </h1>
        <p className="max-w-2xl text-lg text-muted-foreground">
          {t('home.heroSubtitle')}
        </p>
        {data ? (
          <p className="text-sm text-muted-foreground">
            {formatDateTime(data.start)} {t('home.windowTo')} {formatDateTime(data.end)}
          </p>
        ) : (
          <Skeleton className="h-5 w-72" />
        )}
        <div className="flex flex-wrap gap-2">
          {suggestionsFor('home').map((suggestion) => (
            <Button
              key={suggestion}
              variant="outline"
              size="sm"
              className="h-auto rounded-full px-3 py-1.5 whitespace-normal"
              onClick={() => startChat(suggestion)}
            >
              {suggestion}
            </Button>
          ))}
        </div>
      </section>
      <Overview />
      <Explorer />
    </div>
  )
}
