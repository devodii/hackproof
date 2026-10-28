import { Badge } from '@/components/ui/badge'
import { tierLabel } from '@/lib/format'
import type { Tier } from '@/lib/types'

const styles: Record<Tier, string> = {
  verified: 'border-transparent bg-primary text-primary-foreground',
  likely: 'border-primary bg-transparent text-foreground',
  possible: 'border-border bg-transparent text-muted-foreground',
  unattributed: 'border-border bg-transparent text-muted-foreground',
}

export function TierBadge({ tier }: { tier: Tier }) {
  return (
    <Badge variant="outline" className={styles[tier]}>
      {tierLabel[tier]}
    </Badge>
  )
}
