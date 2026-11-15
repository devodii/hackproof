import { animate, motion, useMotionValue, useTransform } from 'motion/react'
import { useEffect } from 'react'

import { useStill } from '@/components/wrapped/use-still'
import { formatNumber } from '@/lib/format'
import { EASE_SETTLE } from '@/lib/wrapped'

interface FigureProps {
  value: number
  delay?: number
  className?: string
}

export function Figure({ value, delay = 0, className }: FigureProps) {
  const still = useStill()
  const count = useMotionValue(still ? value : 0)
  const text = useTransform(count, (latest) => formatNumber(Math.round(latest)))

  useEffect(() => {
    if (still) return
    const controls = animate(count, value, { duration: 1.6, delay, ease: EASE_SETTLE })
    return controls.stop
  }, [count, value, delay, still])

  return <motion.span className={className}>{text}</motion.span>
}
