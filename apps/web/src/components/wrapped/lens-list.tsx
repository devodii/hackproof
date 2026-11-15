import { motion } from 'motion/react'

import { useStill } from '@/components/wrapped/use-still'
import { formatNumber } from '@/lib/format'
import { EASE_OUT, isSameLens, percent, type Lens } from '@/lib/wrapped'
import { cn } from '@/lib/utils'

export interface LensRow {
  label: string
  value: number
  lens: Lens
}

interface LensListProps {
  rows: LensRow[]
  total: number
  active: Lens | null
  onSelect: (lens: Lens) => void
  delay?: number
}

export function LensList({ rows, total, active, onSelect, delay = 0 }: LensListProps) {
  const still = useStill()

  return (
    <ul className="flex flex-1 flex-col justify-around gap-1">
      {rows.map((row, index) => {
        const selected = isSameLens(active, row.lens)

        return (
          <li key={`${row.lens.kind}:${row.lens.value}`}>
            <button
              type="button"
              onClick={() => onSelect(row.lens)}
              aria-pressed={selected}
              className={cn(
                'group lens-row w-full items-center gap-3 rounded-md px-1.5 py-1 text-left transition-colors hover:bg-tile-border',
                selected && 'bg-tile-border',
              )}
            >
              <span
                className={cn(
                  'truncate text-sm',
                  selected ? 'font-semibold text-primary' : 'text-foreground/80',
                )}
              >
                {row.label}
              </span>
              <span className="h-2 overflow-hidden rounded-full bg-track">
                <motion.span
                  initial={still ? false : { scaleX: 0 }}
                  animate={{ scaleX: 1 }}
                  transition={{
                    delay: delay + index * 0.08,
                    duration: 0.9,
                    ease: EASE_OUT,
                  }}
                  style={{ width: `${percent(row.value, total)}%`, originX: 0 }}
                  className={cn(
                    'block h-full rounded-full',
                    selected ? 'bg-primary' : 'bg-secondary',
                  )}
                />
              </span>
              <span className="text-right text-sm font-semibold tabular-nums">
                {formatNumber(row.value)}
              </span>
            </button>
          </li>
        )
      })}
    </ul>
  )
}
