import { motion } from 'motion/react'

import { Reveal } from '@/components/integration/reveal'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'
import { formatNumber } from '@/lib/format'
import type { CaptureCount, ContractState } from '@/lib/types'
import { EASE_OUT } from '@/lib/wrapped'

interface CaptureDemandProps {
  rows: CaptureCount[]
  contracts: ContractState[]
}

export function CaptureDemand({ rows, contracts }: CaptureDemandProps) {
  const max = Math.max(...rows.map((row) => row.projects), 1)
  const tracked = rows.some((row) => row.offered_by.length || row.expired_on.length)
  const name = (slug: string) => {
    const contract = contracts.find((item) => item.slug === slug)
    return contract ? `${contract.name} · ${contract.network}` : slug
  }

  return (
    <Reveal>
      <Card>
        <CardContent className="grid gap-x-10 gap-y-4 md:grid-cols-2">
          {rows.map((row, index) => (
            <div key={row.value} className="flex flex-col gap-1.5">
              <div className="flex items-baseline justify-between gap-3">
                <span className="truncate font-mono text-sm">{row.value}</span>
                <span className="font-heading tabular-nums">{formatNumber(row.projects)}</span>
              </div>
              <div className="h-1.5 w-full overflow-hidden rounded-full bg-track">
                <motion.div
                  initial={{ width: 0 }}
                  whileInView={{ width: `${(row.projects / max) * 100}%` }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.9, delay: Math.min(index, 8) * 0.04, ease: EASE_OUT }}
                  className="h-full rounded-full bg-primary"
                />
              </div>
              {tracked && (
                <div className="flex flex-wrap gap-1.5">
                  {row.offered_by.map((slug) => (
                    <Badge key={slug} variant="outline">
                      {name(slug)}
                    </Badge>
                  ))}
                  {row.expired_on.map((slug) => (
                    <Badge key={slug} variant="destructive">
                      Expired on {name(slug)}
                    </Badge>
                  ))}
                  {!row.offered_by.length && !row.expired_on.length && (
                    <Badge variant="destructive">Not offered</Badge>
                  )}
                </div>
              )}
            </div>
          ))}
        </CardContent>
      </Card>
    </Reveal>
  )
}
