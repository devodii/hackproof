import { CrownIcon, MedalIcon } from 'lucide-react'

import { Badge } from '@/components/ui/badge'
import { placeLabel } from '@/lib/format'
import type { Place } from '@/lib/types'

const styles = {
  first: {
    icon: CrownIcon,
    className: 'border-amber-500/50 bg-amber-500/10 text-amber-600 dark:text-amber-400',
  },
  'runner-up': {
    icon: MedalIcon,
    className: 'border-slate-400/60 bg-slate-400/10 text-slate-600 dark:text-slate-300',
  },
} as const

export function AwardBadge({ place }: { place: Place | null }) {
  if (!place) return null
  const { icon: Icon, className } = styles[place]

  return (
    <Badge variant="outline" className={className}>
      <Icon />
      {placeLabel[place]}
    </Badge>
  )
}
