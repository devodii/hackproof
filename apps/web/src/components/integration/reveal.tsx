import { motion } from 'motion/react'
import type { ReactNode } from 'react'

import { cn } from '@/lib/utils'
import { EASE_OUT } from '@/lib/wrapped'

interface RevealProps {
  delay?: number
  className?: string
  children: ReactNode
}

export function Reveal({ delay = 0, className, children }: RevealProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20, filter: 'blur(6px)' }}
      whileInView={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
      viewport={{ once: true, margin: '0px 0px -8% 0px' }}
      transition={{ duration: 0.7, delay, ease: EASE_OUT }}
      className={cn(className)}
    >
      {children}
    </motion.div>
  )
}
