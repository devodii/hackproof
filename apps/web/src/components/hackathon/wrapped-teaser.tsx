import { motion, useReducedMotion } from 'motion/react'
import { ArrowRightIcon, SparklesIcon } from 'lucide-react'

import { CountUp } from '@/components/count-up'
import { Link } from '@/components/hackathon/hackathon-link'
import { useHackathon } from '@/hooks/use-hackathon'
import { useProjects } from '@/hooks/use-projects'
import { useStats } from '@/hooks/use-stats'
import { cn } from '@/lib/utils'

const TILES = 288

const tile = {
  rest: { scale: 1 },
  hover: (index: number) => ({
    scale: [1, 1.5, 1],
    transition: { delay: (index % 24) * 0.018 + Math.floor(index / 24) * 0.03, duration: 0.5 },
  }),
}

export function WrappedTeaser() {
  const reduced = useReducedMotion()
  const { name } = useHackathon()
  const { data: projects = [] } = useProjects()
  const { data: stats } = useStats()
  const tiles = Array.from(
    { length: TILES },
    (_, index) => projects[index % Math.max(projects.length, 1)],
  )

  return (
    <motion.div initial="rest" whileHover={reduced ? undefined : 'hover'} animate="rest">
      <Link
        to="/wrapped"
        className="group relative flex h-full flex-col gap-6 overflow-hidden rounded-xl bg-card p-6 text-card-foreground ring-1 ring-foreground/10 transition-shadow hover:ring-primary/60"
      >
        <div
          aria-hidden
          className="grid flex-1 content-start gap-1 transition-opacity"
          style={{ gridTemplateColumns: 'repeat(24, minmax(0, 1fr))' }}
        >
          {tiles.map((project, index) => (
            <motion.span
              key={index}
              custom={index}
              variants={tile}
              className={cn(
                'aspect-square rounded-[3px]',
                index % 7 === 0 && 'animate-pulse',
                !project && 'bg-muted',
                project?.tier === 'verified' && 'bg-primary',
                project && project.tier !== 'verified' && 'bg-primary/35',
              )}
            />
          ))}
        </div>
        <div className="flex items-end justify-between gap-4">
          <div className="flex flex-col gap-1">
            <span className="inline-flex items-center gap-1.5 text-sm text-muted-foreground">
              <SparklesIcon className="size-3.5" /> Wrapped
            </span>
            <span translate="no" className="font-heading text-3xl leading-tight">
              {name}, wrapped
            </span>
            {stats && (
              <span className="text-sm text-muted-foreground">
                <CountUp value={stats.projects} /> projects and{' '}
                <CountUp value={stats.contributors} /> builders in one poster
              </span>
            )}
          </div>
          <span className="inline-flex size-10 shrink-0 items-center justify-center rounded-full bg-primary text-primary-foreground transition-transform group-hover:translate-x-1">
            <ArrowRightIcon className="size-5" />
          </span>
        </div>
      </Link>
    </motion.div>
  )
}
