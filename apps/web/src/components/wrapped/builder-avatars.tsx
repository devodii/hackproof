import { motion } from 'motion/react'
import { Link } from 'react-router'

import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip'
import { useStill } from '@/components/wrapped/use-still'
import { formatNumber } from '@/lib/format'
import type { WrappedBuilder } from '@/lib/types'
import { EASE_SPRING } from '@/lib/wrapped'

interface BuilderAvatarsProps {
  builders: WrappedBuilder[]
  size?: 'default' | 'sm' | 'lg'
  delay?: number
}

export function BuilderAvatars({ builders, size = 'default', delay = 0 }: BuilderAvatarsProps) {
  const still = useStill()

  return (
    <ul className="flex flex-wrap gap-1.5">
      {builders.map((builder, index) => (
        <motion.li
          key={builder.login}
          initial={still ? false : { opacity: 0, scale: 0.3 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: delay + index * 0.05, duration: 0.5, ease: EASE_SPRING }}
        >
          <Tooltip>
            <TooltipTrigger
              render={
                <Link
                  to={`/contributor/${encodeURIComponent(builder.login)}`}
                  aria-label={builder.login}
                  className="block rounded-full ring-2 ring-tile-border transition-transform hover:scale-110 hover:ring-primary"
                />
              }
            >
              <Avatar size={size}>
                {builder.avatar_url && <AvatarImage src={builder.avatar_url} alt="" />}
                <AvatarFallback>{builder.login.slice(0, 2).toUpperCase()}</AvatarFallback>
              </Avatar>
            </TooltipTrigger>
            <TooltipContent>
              <span className="font-semibold">{builder.login}</span>
              <span className="opacity-70">
                {formatNumber(builder.contributions)} commits · {builder.projects}{' '}
                {builder.projects === 1 ? 'project' : 'projects'}
              </span>
            </TooltipContent>
          </Tooltip>
        </motion.li>
      ))}
    </ul>
  )
}
