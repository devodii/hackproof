import { motion } from 'motion/react'

import { useStill } from '@/components/wrapped/use-still'
import { EASE_OUT, isSameLens, percent, type Lens } from '@/lib/wrapped'
import type { Count } from '@/lib/types'
import { cn } from '@/lib/utils'

const SEGMENTS = ['bg-primary', 'bg-secondary', 'bg-chart-2', 'bg-chart-4', 'bg-muted-foreground']

interface SegmentedBarProps {
  data: Count[]
  active: Lens | null
  onSelect: (lens: Lens) => void
  delay?: number
}

export function SegmentedBar({ data, active, onSelect, delay = 0 }: SegmentedBarProps) {
  const still = useStill()
  const total = data.reduce((sum, item) => sum + item.value, 0)
  const lensOf = (label: string): Lens => ({ kind: 'language', value: label })

  return (
    <div>
      <div className="flex h-4 gap-0.5 overflow-hidden rounded-md">
        {data.map((item, index) => (
          <motion.button
            key={item.label}
            type="button"
            onClick={() => onSelect(lensOf(item.label))}
            aria-label={item.label}
            initial={still ? false : { scaleX: 0 }}
            animate={{ scaleX: 1 }}
            transition={{ delay: delay + index * 0.12, duration: 0.9, ease: EASE_OUT }}
            style={{ width: `${percent(item.value, total)}%`, originX: 0 }}
            className={cn(
              'rounded-sm transition-opacity hover:opacity-80',
              SEGMENTS[index],
              active?.kind === 'language' &&
                !isSameLens(active, lensOf(item.label)) &&
                'opacity-30',
            )}
          />
        ))}
      </div>
      <ul className="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-xs">
        {data.map((item, index) => (
          <li key={item.label} className="flex items-center gap-1.5">
            <i className={cn('size-2 rounded-full', SEGMENTS[index])} />
            <span className="text-foreground/80">{item.label}</span>
            <span className="font-semibold tabular-nums">{percent(item.value, total)}%</span>
          </li>
        ))}
      </ul>
    </div>
  )
}
