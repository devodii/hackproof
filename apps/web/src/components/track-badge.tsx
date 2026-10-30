import { SproutIcon, TrendingUpIcon } from 'lucide-react'

import { Badge } from '@/components/ui/badge'
import { trackLabel } from '@/lib/format'
import type { Track } from '@/lib/types'

const icons = { genesis: SproutIcon, scale: TrendingUpIcon } as const

export function TrackBadge({ track }: { track: Track | null | undefined }) {
  if (!track) return null
  const Icon = icons[track]

  return (
    <Badge variant="outline" className="text-muted-foreground">
      <Icon />
      {trackLabel[track]}
    </Badge>
  )
}
