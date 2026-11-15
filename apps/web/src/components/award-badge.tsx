import { Badge } from '@/components/ui/badge'
import { awardIcon } from '@/components/award-mark'
import { placeLabel } from '@/lib/format'
import type { Place } from '@/lib/types'

const styles = {
  first: 'border-award-first/50 bg-award-first/10 text-award-first',
  'runner-up': 'border-award-runner-up/60 bg-award-runner-up/10 text-award-runner-up',
} as const

export function AwardBadge({ place }: { place: Place | null }) {
  if (!place) return null
  const Icon = awardIcon[place]

  return (
    <Badge variant="outline" className={styles[place]}>
      <Icon />
      {placeLabel[place]}
    </Badge>
  )
}
