import { motion, useReducedMotion } from 'motion/react'
import { ArrowRightIcon } from 'lucide-react'

import { AwardBadge } from '@/components/award-badge'
import { AwardedAvatar } from '@/components/award-mark'
import { Link } from '@/components/hackathon/hackathon-link'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { useProjects } from '@/hooks/use-projects'
import { projectName } from '@/lib/format'

export function WinnersSpotlight() {
  const reduced = useReducedMotion()
  const { data, isPending } = useProjects()
  const winners = (data ?? [])
    .filter((project) => project.award !== null)
    .sort((a, b) => (a.award === 'first' ? -1 : 0) - (b.award === 'first' ? -1 : 0))

  if (!isPending && winners.length === 0) return null

  return (
    <Card>
      <CardHeader>
        <CardDescription>Winners</CardDescription>
        <CardTitle className="font-heading text-3xl">Who took the prizes</CardTitle>
      </CardHeader>
      <CardContent className="flex flex-1 flex-col gap-4">
        <ul className="flex flex-col gap-1">
          {isPending
            ? Array.from({ length: 4 }, (_, index) => (
                <li key={index}>
                  <Skeleton className="h-11 w-full" />
                </li>
              ))
            : winners.map((project, index) => (
                <motion.li
                  key={project.project_id}
                  initial={reduced ? false : { opacity: 0, x: -12 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.06, duration: 0.35 }}
                >
                  <Link
                    to={`/project/${project.project_id}`}
                    className="flex items-center gap-3 rounded-lg px-2 py-1.5 transition-colors hover:bg-muted"
                  >
                    <AwardedAvatar place={project.award}>
                      <Avatar>
                        {project.owner_avatar && <AvatarImage src={project.owner_avatar} alt="" />}
                        <AvatarFallback>
                          {projectName(project.project_id).slice(0, 2).toUpperCase()}
                        </AvatarFallback>
                      </Avatar>
                    </AwardedAvatar>
                    <span translate="no" className="min-w-0 flex-1 truncate font-medium">
                      {projectName(project.project_id)}
                    </span>
                    <AwardBadge place={project.award} />
                  </Link>
                </motion.li>
              ))}
        </ul>
        <Link
          to="/?award=first&award=runner-up"
          className="group mt-auto inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground"
        >
          Compare the winners
          <ArrowRightIcon className="size-3.5 transition-transform group-hover:translate-x-0.5" />
        </Link>
      </CardContent>
    </Card>
  )
}
