import { motion } from 'motion/react'

import { Reveal } from '@/components/integration/reveal'
import { Card, CardContent } from '@/components/ui/card'
import { formatNumber, humanize } from '@/lib/format'
import type { SignalCount } from '@/lib/types'
import { EASE_OUT } from '@/lib/wrapped'

interface SignalBarsProps {
  signals: SignalCount[]
  max: number
}

function Row({ signal, max, index }: { signal: SignalCount; max: number; index: number }) {
  const share = max > 0 ? (signal.projects / max) * 100 : 0

  return (
    <div className="flex flex-col gap-1.5">
      <div className="flex items-baseline justify-between gap-3 text-sm">
        <span className={signal.projects ? '' : 'text-muted-foreground'}>{signal.label}</span>
        <span className="font-heading tabular-nums">{formatNumber(signal.projects)}</span>
      </div>
      <div className="h-1.5 w-full overflow-hidden rounded-full bg-track">
        <motion.div
          initial={{ width: 0 }}
          whileInView={{ width: `${share}%` }}
          viewport={{ once: true }}
          transition={{ duration: 0.9, delay: index * 0.05, ease: EASE_OUT }}
          className="h-full rounded-full bg-primary"
        />
      </div>
    </div>
  )
}

export function SignalBars({ signals, max }: SignalBarsProps) {
  const groups = signals.reduce<Record<string, SignalCount[]>>((found, signal) => {
    ;(found[signal.group] ??= []).push(signal)
    return found
  }, {})

  return (
    <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
      {Object.entries(groups).map(([group, items], index) => (
        <Reveal key={group} delay={Math.min(index, 5) * 0.06} className="h-full">
          <Card className="h-full">
            <CardContent className="flex flex-col gap-4">
              <h3 className="text-eyebrow font-semibold tracking-eyebrow text-muted-foreground uppercase">
                {humanize(group)}
              </h3>
              {items.map((signal, row) => (
                <Row key={signal.slug} signal={signal} max={max} index={row} />
              ))}
            </CardContent>
          </Card>
        </Reveal>
      ))}
    </div>
  )
}
