import { animate, motion, useMotionValue, useReducedMotion, useTransform } from 'motion/react'
import { useEffect } from 'react'

import { formatNumber } from '@/lib/format'

export function CountUp({ value }: { value: number }) {
  const reduced = useReducedMotion()
  const count = useMotionValue(reduced ? value : 0)
  const text = useTransform(count, (latest) => formatNumber(Math.round(latest)))

  useEffect(() => {
    const controls = animate(count, value, { duration: 1.1, ease: 'easeOut' })
    return controls.stop
  }, [count, value])

  return <motion.span>{text}</motion.span>
}
