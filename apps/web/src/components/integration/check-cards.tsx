import { motion } from 'motion/react'
import { Link } from 'react-router'

import { SeverityIcon } from '@/components/integration/check-status'
import { Reveal } from '@/components/integration/reveal'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Card, CardContent } from '@/components/ui/card'
import { formatNumber } from '@/lib/format'
import type { Adopter, CheckCount } from '@/lib/types'
import { cn } from '@/lib/utils'
import { EASE_OUT } from '@/lib/wrapped'

interface CheckCardsProps {
  checks: CheckCount[]
  adopters: Adopter[]
}

const SEVERITY_BAR = { warn: 'bg-warn', fail: 'bg-destructive' }

function Meter({
  passing,
  failing,
  severity,
}: Pick<CheckCount, 'passing' | 'failing' | 'severity'>) {
  const total = passing + failing
  const bad = total ? (failing / total) * 100 : 0

  return (
    <div className="flex h-2 w-full overflow-hidden rounded-full bg-track">
      <motion.div
        initial={{ width: 0 }}
        whileInView={{ width: `${100 - bad}%` }}
        viewport={{ once: true }}
        transition={{ duration: 1, ease: EASE_OUT }}
        className="h-full bg-ok"
      />
      <motion.div
        initial={{ width: 0 }}
        whileInView={{ width: `${bad}%` }}
        viewport={{ once: true }}
        transition={{ duration: 1, delay: 0.15, ease: EASE_OUT }}
        className={cn('h-full', SEVERITY_BAR[severity])}
      />
    </div>
  )
}

export function CheckCards({ checks, adopters }: CheckCardsProps) {
  const byName = new Map(adopters.map((adopter) => [adopter.full_name, adopter]))
  const ordered = [...checks].sort((a, b) => b.failing - a.failing)

  return (
    <div className="grid gap-3 lg:grid-cols-2">
      {ordered.map((check, index) => (
        <Reveal key={check.slug} delay={Math.min(index, 5) * 0.06} className="h-full">
          <Card className="h-full">
            <CardContent className="flex h-full flex-col gap-4">
              <div className="flex items-start gap-3">
                <SeverityIcon severity={check.severity} />
                <span className="font-medium">{check.label}</span>
              </div>
              <div className="flex items-end justify-between gap-4">
                <span className="font-heading text-stat">
                  {formatNumber(check.failing)}
                  <span className="text-base text-muted-foreground">
                    {' '}
                    of {formatNumber(check.failing + check.passing)} projects
                  </span>
                </span>
              </div>
              <Meter passing={check.passing} failing={check.failing} severity={check.severity} />
              {check.offenders.length > 0 && (
                <div className="flex flex-wrap gap-1.5">
                  {check.offenders.map((name) => {
                    const adopter = byName.get(name)
                    if (!adopter) return null
                    return (
                      <Link
                        key={name}
                        to={`/project/${adopter.project_id}`}
                        className="inline-flex items-center gap-1.5 rounded-full border py-0.5 pr-2.5 pl-0.5 text-xs hover:bg-muted"
                      >
                        <Avatar size="sm">
                          {adopter.owner_avatar && (
                            <AvatarImage src={adopter.owner_avatar} alt="" />
                          )}
                          <AvatarFallback>{adopter.owner.slice(0, 2).toUpperCase()}</AvatarFallback>
                        </Avatar>
                        {name.split('/')[1]}
                      </Link>
                    )
                  })}
                </div>
              )}
            </CardContent>
          </Card>
        </Reveal>
      ))}
    </div>
  )
}
