import { motion } from 'motion/react'
import type { ReactNode } from 'react'

import { useStill } from '@/components/wrapped/use-still'
import { cn } from '@/lib/utils'
import { EASE_OUT } from '@/lib/wrapped'

interface TileProps {
  title: string
  note?: ReactNode
  delay?: number
  grow?: number
  className?: string
  children: ReactNode
}

export function Tile({ title, note, delay = 0, grow, className, children }: TileProps) {
  const still = useStill()

  return (
    <motion.section
      initial={still ? false : { opacity: 0, y: 22, filter: 'blur(8px)' }}
      animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
      transition={{ duration: 0.8, delay, ease: EASE_OUT }}
      style={{ flexGrow: grow }}
      className={cn(
        'flex min-h-0 flex-col rounded-2xl border border-tile-border bg-tile p-5 shadow-tile',
        className,
      )}
    >
      <header className="mb-3 flex items-baseline justify-between gap-3">
        <h2 className="text-eyebrow font-semibold tracking-eyebrow text-muted-foreground uppercase">
          {title}
        </h2>
        {note && <span className="text-eyebrow text-muted-foreground">{note}</span>}
      </header>
      {children}
    </motion.section>
  )
}
