import type { ToolingItem } from '@/lib/types'

interface DistributionBarProps {
  items: ToolingItem[]
  maxCount?: number
  className?: string
}

const BAR_COLORS = [
  'bg-emerald-500',
  'bg-blue-500',
  'bg-violet-500',
  'bg-amber-500',
  'bg-rose-500',
  'bg-cyan-500',
  'bg-fuchsia-500',
  'bg-indigo-500',
]

export function DistributionBar({ items, maxCount, className = '' }: DistributionBarProps) {
  const highest = maxCount ?? Math.max(...items.map((i) => i.count), 1)

  return (
    <div className={`flex flex-col gap-3 ${className}`}>
      {items.map((item, index) => {
        const color = BAR_COLORS[index % BAR_COLORS.length]
        const widthPct = Math.min(100, Math.max(2, (item.count / highest) * 100))

        return (
          <div key={item.name} className="flex flex-col gap-1.5">
            <div className="flex items-center justify-between text-xs sm:text-sm">
              <span className="font-medium text-foreground">{item.name}</span>
              <div className="flex items-center gap-2">
                <span className="font-mono text-muted-foreground">{item.count}</span>
                <span className="font-mono text-xs text-muted-foreground/80">
                  ({item.percentage}%)
                </span>
              </div>
            </div>
            <div className="h-2.5 w-full overflow-hidden rounded-full bg-muted">
              <div
                className={`h-full rounded-full transition-all duration-500 ${color}`}
                style={{ width: `${widthPct}%` }}
                title={`${item.name}: ${item.count} (${item.percentage}%)`}
              />
            </div>
          </div>
        )
      })}
    </div>
  )
}
