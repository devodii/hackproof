import { motion } from 'motion/react'

import { awardIcon } from '@/components/award-mark'
import { useHackathonPath } from '@/hooks/use-hackathon'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip'
import { useStill } from '@/components/wrapped/use-still'
import { placeLabel, projectName, tierLabel } from '@/lib/format'
import { EASE_SPRING, matchesLens, type Lens } from '@/lib/wrapped'
import type { Place, Project } from '@/lib/types'
import { cn } from '@/lib/utils'

function AwardGlyph({ place }: { place: Place }) {
  const Icon = awardIcon[place]

  return <Icon className="size-3/5 fill-award-foreground/25 text-award-foreground" />
}

interface WaffleProps {
  projects: Project[]
  lens: Lens | null
  columns: number
  delay?: number
}

export function Waffle({ projects, lens, columns, delay = 0 }: WaffleProps) {
  const still = useStill()
  const path = useHackathonPath()

  return (
    <div className="grid gap-1" style={{ gridTemplateColumns: `repeat(${columns}, 1fr)` }}>
      {projects.map((project, index) => {
        const name = projectName(project.project_id)
        const dimmed = lens !== null && !matchesLens(project, lens)

        return (
          <Tooltip key={project.project_id}>
            <TooltipTrigger
              render={
                <a
                  href={path(`/project/${project.project_id}`)}
                  target="_blank"
                  rel="noreferrer"
                  aria-label={name}
                  className={cn(
                    'aspect-square rounded-sm transition-all duration-300 hover:scale-125',
                    dimmed && 'opacity-15',
                  )}
                />
              }
            >
              <motion.span
                initial={still ? false : { opacity: 0, scale: 0.2 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{
                  delay: delay + (index % columns) * 0.018 + Math.floor(index / columns) * 0.045,
                  duration: 0.45,
                  ease: EASE_SPRING,
                }}
                className={cn(
                  'grid size-full place-items-center rounded-sm',
                  project.tier === 'verified' ? 'bg-primary' : 'bg-secondary',
                )}
              >
                {project.award && <AwardGlyph place={project.award} />}
              </motion.span>
            </TooltipTrigger>
            <TooltipContent>
              <Avatar size="sm">
                {project.owner_avatar && <AvatarImage src={project.owner_avatar} alt="" />}
                <AvatarFallback>{name.slice(0, 2).toUpperCase()}</AvatarFallback>
              </Avatar>
              <span className="font-semibold">{name}</span>
              {project.award && <span>{placeLabel[project.award]}</span>}
              <span className="opacity-70">
                {tierLabel[project.tier]}
                {project.language && ` · ${project.language}`}
              </span>
            </TooltipContent>
          </Tooltip>
        )
      })}
    </div>
  )
}
