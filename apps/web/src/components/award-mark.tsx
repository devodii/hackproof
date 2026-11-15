import { CrownIcon, MedalIcon } from 'lucide-react'
import type { ReactNode } from 'react'

import { placeLabel } from '@/lib/format'
import type { Place } from '@/lib/types'
import { cn } from '@/lib/utils'

export const awardIcon = {
  first: CrownIcon,
  'runner-up': MedalIcon,
} as const

const tone = {
  first: 'text-award-first',
  'runner-up': 'text-award-runner-up',
} as const

export function AwardMark({ place, className }: { place: Place | null; className?: string }) {
  if (!place) return null
  const Icon = awardIcon[place]

  return (
    <span title={placeLabel[place]} className={cn('inline-flex shrink-0', tone[place], className)}>
      <Icon className="size-full fill-current/25" aria-label={placeLabel[place]} />
    </span>
  )
}

export function AwardedAvatar({
  place,
  children,
  className,
}: {
  place: Place | null
  children: ReactNode
  className?: string
}) {
  return (
    <span className={cn('relative inline-flex shrink-0', className)}>
      {children}
      {place === 'first' && (
        <AwardMark
          place={place}
          className="absolute -top-2.5 left-1/2 size-5 -translate-x-1/2 -rotate-12 drop-shadow-sm"
        />
      )}
      {place === 'runner-up' && (
        <span className="absolute -right-1 -bottom-1 grid size-4 place-items-center rounded-full bg-background ring-1 ring-border">
          <AwardMark place={place} className="size-3" />
        </span>
      )}
    </span>
  )
}
