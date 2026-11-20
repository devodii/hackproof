import { ArrowUpRightIcon } from 'lucide-react'
import { useState } from 'react'
import { Link } from '@/components/hackathon/hackathon-link'

import { CheckStatus } from '@/components/integration/check-status'
import { Reveal } from '@/components/integration/reveal'
import { TierBadge } from '@/components/tier-badge'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { projectName } from '@/lib/format'
import type { Adopter } from '@/lib/types'

const SIGNALS_SHOWN = 5
const CAPTURES_SHOWN = 4
const INITIAL = 12

function AdopterCard({ adopter }: { adopter: Adopter }) {
  const signals = adopter.profile.signals
  const captures = Object.values(adopter.profile.captures).flat()

  return (
    <Link to={`/project/${adopter.project_id}`} className="group block h-full">
      <Card className="h-full transition-all group-hover:-translate-y-0.5 group-hover:ring-primary/50">
        <CardContent className="flex h-full flex-col gap-3">
          <div className="flex items-start justify-between gap-3">
            <div className="flex min-w-0 items-center gap-3">
              <Avatar>
                {adopter.owner_avatar && <AvatarImage src={adopter.owner_avatar} alt="" />}
                <AvatarFallback>{adopter.owner.slice(0, 2).toUpperCase()}</AvatarFallback>
              </Avatar>
              <div className="flex min-w-0 flex-col">
                <span translate="no" className="truncate font-medium">
                  {projectName(adopter.project_id)}
                </span>
                <span className="text-xs text-muted-foreground">
                  {adopter.language ?? 'Unknown'}
                </span>
              </div>
            </div>
            <ArrowUpRightIcon className="size-4 shrink-0 text-muted-foreground transition-colors group-hover:text-primary" />
          </div>
          <div className="flex flex-wrap gap-1.5">
            <TierBadge tier={adopter.tier} />
            {signals.slice(0, SIGNALS_SHOWN).map((signal) => (
              <Badge key={signal.slug} variant="outline">
                {signal.label}
              </Badge>
            ))}
            {signals.length > SIGNALS_SHOWN && (
              <Badge variant="secondary">+{signals.length - SIGNALS_SHOWN}</Badge>
            )}
          </div>
          {captures.length > 0 && (
            <span className="truncate font-mono text-xs text-muted-foreground">
              {captures.slice(0, CAPTURES_SHOWN).join(' · ')}
            </span>
          )}
          {adopter.profile.checks.length > 0 && (
            <span className="mt-auto flex gap-1.5">
              {adopter.profile.checks.map((check) => (
                <CheckStatus key={check.slug} check={check} />
              ))}
            </span>
          )}
        </CardContent>
      </Card>
    </Link>
  )
}

export function AdopterCards({ adopters }: { adopters: Adopter[] }) {
  const [all, setAll] = useState(false)
  const shown = all ? adopters : adopters.slice(0, INITIAL)

  return (
    <div className="flex flex-col gap-4">
      <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
        {shown.map((adopter, index) => (
          <Reveal key={adopter.project_id} delay={Math.min(index, 5) * 0.05} className="h-full">
            <AdopterCard adopter={adopter} />
          </Reveal>
        ))}
      </div>
      {adopters.length > INITIAL && !all && (
        <Button variant="outline" className="self-center" onClick={() => setAll(true)}>
          Show all {adopters.length} projects
        </Button>
      )}
    </div>
  )
}
