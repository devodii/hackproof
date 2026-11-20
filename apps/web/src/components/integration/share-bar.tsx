import { motion } from 'motion/react'

import { EASE_OUT } from '@/lib/wrapped'

export function ShareBar({ value, max }: { value: number; max: number }) {
  const share = max > 0 ? (value / max) * 100 : 0

  return (
    <div className="h-1.5 w-24 overflow-hidden rounded-full bg-track">
      <motion.div
        initial={{ width: 0 }}
        whileInView={{ width: `${share}%` }}
        viewport={{ once: true }}
        transition={{ duration: 0.9, ease: EASE_OUT }}
        className="h-full rounded-full bg-primary"
      />
    </div>
  )
}
