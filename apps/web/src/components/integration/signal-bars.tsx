import { Bar } from '@/components/integration/bar'
import { formatNumber, humanize } from '@/lib/format'
import type { SignalCount } from '@/lib/types'

interface SignalBarsProps {
  signals: SignalCount[]
  max: number
}

export function SignalBars({ signals, max }: SignalBarsProps) {
  const groups = signals.reduce<Record<string, SignalCount[]>>((found, signal) => {
    ;(found[signal.group] ??= []).push(signal)
    return found
  }, {})

  return (
    <div className="grid gap-6 md:grid-cols-2">
      {Object.entries(groups).map(([group, items]) => (
        <div key={group} className="flex flex-col gap-3">
          <h3 className="text-sm font-medium text-muted-foreground">{humanize(group)}</h3>
          {items.map((signal) => (
            <div key={signal.slug} className="flex flex-col gap-1">
              <div className="flex justify-between gap-3 text-sm">
                <span>{signal.label}</span>
                <span className="tabular-nums text-muted-foreground">
                  {formatNumber(signal.projects)}
                </span>
              </div>
              <Bar value={signal.projects} max={max} />
            </div>
          ))}
        </div>
      ))}
    </div>
  )
}
