import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip'
import { flagEmoji } from '@/lib/format'
import type { Contributor } from '@/lib/types'

const VISIBLE = 30

export function Contributors({ contributors }: { contributors: Contributor[] }) {
  const hidden = contributors.length - VISIBLE

  return (
    <div className="flex flex-wrap items-center gap-2">
      {contributors.slice(0, VISIBLE).map((person) => (
        <Tooltip key={person.login}>
          <TooltipTrigger
            render={
              <a href={person.url} target="_blank" rel="noreferrer" aria-label={person.login} />
            }
          >
            <Avatar>
              {person.avatar_url && <AvatarImage src={person.avatar_url} alt={person.login} />}
              <AvatarFallback>{person.login.slice(0, 2).toUpperCase()}</AvatarFallback>
            </Avatar>
          </TooltipTrigger>
          <TooltipContent>
            {person.login}
            {person.country && ` ${flagEmoji(person.country)}`} · {person.contributions} commits
          </TooltipContent>
        </Tooltip>
      ))}
      {hidden > 0 && <span className="text-sm text-muted-foreground">+{hidden} more</span>}
    </div>
  )
}
