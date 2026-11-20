import { useSearchParams } from 'react-router'

import { suggestionsFor } from '@/components/chat/page'
import { useChatPanel } from '@/components/chat/use-chat-panel'
import { Explorer } from '@/components/explorer/explorer'
import { FilterHeading } from '@/components/explorer/filter-heading'
import { readSelection, selectedCount } from '@/components/explorer/filters'
import { WinnersSpotlight } from '@/components/hackathon/winners-spotlight'
import { WrappedTeaser } from '@/components/hackathon/wrapped-teaser'
import { Overview } from '@/components/overview'
import { Button } from '@/components/ui/button'
import { useHackathon } from '@/hooks/use-hackathon'
import { formatDateRange, splitYear } from '@/lib/format'

export function HomePage() {
  const hackathon = useHackathon()
  const { title, year } = splitYear(hackathon.name)
  const { startChat } = useChatPanel()
  const [params] = useSearchParams()

  if (selectedCount(readSelection(params)) > 0) {
    return (
      <div className="flex flex-col gap-8">
        <FilterHeading />
        <Explorer />
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-10">
      <section className="flex flex-col items-start gap-5">
        <p className="flex flex-wrap items-center gap-x-3 gap-y-1 text-eyebrow font-semibold tracking-eyebrow text-muted-foreground uppercase">
          <span>{formatDateRange(hackathon.starts_at, hackathon.ends_at)}</span>
          {hackathon.location && <span>· {hackathon.location}</span>}
        </p>
        <h1
          translate="no"
          className="max-w-5xl font-heading text-5xl leading-[0.98] text-balance sm:text-8xl"
        >
          {title}
          {year && <span className="text-brand italic"> {year}</span>}
        </h1>
        {hackathon.summary && (
          <p className="max-w-2xl text-lg text-muted-foreground">{hackathon.summary}</p>
        )}
        <div className="flex flex-wrap gap-2">
          {suggestionsFor('home').map((suggestion) => (
            <Button
              key={suggestion}
              variant="outline"
              size="sm"
              className="h-auto max-w-full rounded-full px-3 py-1.5 text-left whitespace-normal"
              onClick={() => startChat(suggestion)}
            >
              {suggestion}
            </Button>
          ))}
        </div>
      </section>
      <section className="grid gap-4 lg:grid-cols-2">
        <WrappedTeaser />
        <WinnersSpotlight />
      </section>
      <Overview />
      <Explorer />
    </div>
  )
}
