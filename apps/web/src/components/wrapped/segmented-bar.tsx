import { motion } from 'motion/react'
import { Link } from 'react-router'

import { useStill } from '@/components/wrapped/use-still'
import { EASE_OUT, type Lens, explorerPath, isSameLens, percent } from '@/lib/wrapped'
import { cn } from '@/lib/utils'

const COLORS = ['bg-primary', 'bg-secondary', 'bg-chart-2', 'bg-chart-4', 'bg-muted-foreground']

export interface Segment {
  label: string
  value: number
  lens?: Lens
}

interface SegmentedBarProps {
  data: Segment[]
  active: Lens | null
  onPreview: (lens: Lens | null) => void
  delay?: number
}

export function SegmentedBar({ data, active, onPreview, delay = 0 }: SegmentedBarProps) {
  const still = useStill()
  const total = data.reduce((sum, item) => sum + item.value, 0)
  const dimmed = (item: Segment) =>
    active?.kind === 'language' && !(item.lens && isSameLens(active, item.lens))

  return (
    <div>
      <div className="flex h-4 gap-0.5 overflow-hidden rounded-md">
        {data.map((item, index) => {
          const segment = (
            <motion.span
              initial={still ? false : { scaleX: 0 }}
              animate={{ scaleX: 1 }}
              transition={{ delay: delay + index * 0.12, duration: 0.9, ease: EASE_OUT }}
              style={{ originX: 0 }}
              className={cn('block size-full rounded-sm transition-opacity', COLORS[index])}
            />
          )

          return (
            <span
              key={item.label}
              style={{ width: `${percent(item.value, total)}%` }}
              className={cn('transition-opacity', dimmed(item) && 'opacity-30')}
            >
              {item.lens ? (
                <Link
                  to={explorerPath(item.lens)}
                  aria-label={item.label}
                  onMouseEnter={() => onPreview(item.lens ?? null)}
                  onMouseLeave={() => onPreview(null)}
                  className="block size-full hover:opacity-80"
                >
                  {segment}
                </Link>
              ) : (
                segment
              )}
            </span>
          )
        })}
      </div>
      <ul className="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-xs">
        {data.map((item, index) => (
          <li key={item.label} className="flex items-center gap-1.5">
            <i className={cn('size-2 rounded-full', COLORS[index])} />
            <span className="text-foreground/80">{item.label}</span>
            <span className="font-semibold tabular-nums">{percent(item.value, total)}%</span>
          </li>
        ))}
      </ul>
    </div>
  )
}
