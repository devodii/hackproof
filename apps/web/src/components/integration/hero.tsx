import { ExternalLinkIcon } from 'lucide-react'
import { motion } from 'motion/react'

import { CountUp } from '@/components/count-up'
import { Badge } from '@/components/ui/badge'
import { formatNumber, humanize } from '@/lib/format'
import type { IntegrationDetail } from '@/lib/types'
import { EASE_OUT } from '@/lib/wrapped'

interface Figure {
  value: number
  label: string
  total?: number
}

function figures(data: IntegrationDetail): Figure[] {
  const findings = data.checks.reduce((sum, check) => sum + check.failing, 0)
  const watched = [...data.contracts, ...data.surfaces]
  const observed = watched.filter((item) => item.snapshot).length
  const expired = data.contracts.reduce((sum, item) => sum + item.expired.length, 0)
  const all: Array<Figure | false | null> = [
    { value: data.adopters.length, total: data.of_projects, label: 'projects using it' },
    { value: findings, label: 'open findings' },
    watched.length > 0 && {
      value: observed,
      total: watched.length,
      label: 'surfaces watched live',
    },
    expired > 0 && { value: expired, label: 'items expired on its contracts' },
    data.overlap && {
      value: data.overlap.matched,
      total: data.overlap.total,
      label: 'hack assets its contracts cover',
    },
  ]
  return all.filter((item): item is Figure => Boolean(item)).slice(0, 4)
}

export function Hero({ data }: { data: IntegrationDetail }) {
  return (
    <header className="relative isolate overflow-hidden rounded-3xl border bg-card px-6 py-10 sm:px-10 sm:py-12">
      <div aria-hidden className="pointer-events-none absolute inset-0 -z-10">
        <div className="absolute -top-60 -left-40 size-glow rounded-full bg-glow-secondary blur-glow" />
        <div className="absolute -right-48 -bottom-72 size-glow-lg rounded-full bg-glow-primary blur-glow-lg" />
        <div className="poster-dots absolute inset-0 opacity-60" />
      </div>
      <motion.div
        initial={{ opacity: 0, y: 14 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.7, ease: EASE_OUT }}
        className="flex flex-col gap-4"
      >
        <div className="flex flex-wrap items-center gap-3">
          <Badge variant="outline">{humanize(data.category)}</Badge>
          <a
            href={data.site}
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground"
          >
            {new URL(data.site).host} <ExternalLinkIcon className="size-3.5" />
          </a>
        </div>
        <h1 className="text-5xl leading-none sm:text-7xl">{data.name}</h1>
        <p className="max-w-2xl text-lg text-muted-foreground">
          How {formatNumber(data.of_projects)} hackathon projects use {data.name}, read from their
          source and checked against what {data.name} runs today.
        </p>
      </motion.div>
      <div className="mt-10 grid grid-cols-2 gap-x-6 gap-y-8 md:grid-cols-4">
        {figures(data).map((item, index) => (
          <motion.div
            key={item.label}
            initial={{ opacity: 0, y: 18 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.15 + index * 0.1, ease: EASE_OUT }}
            className="flex flex-col gap-2 border-l-2 border-primary pl-4"
          >
            <span className="font-heading text-figure sm:text-figure-lg">
              <CountUp value={item.value} />
              {item.total !== undefined && (
                <span className="text-stat text-muted-foreground">
                  {' '}
                  / {formatNumber(item.total)}
                </span>
              )}
            </span>
            <span className="text-sm text-muted-foreground">{item.label}</span>
          </motion.div>
        ))}
      </div>
    </header>
  )
}
