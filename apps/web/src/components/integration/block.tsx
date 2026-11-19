import type { ReactNode } from 'react'

import { Reveal } from '@/components/integration/reveal'

interface BlockProps {
  eyebrow: string
  title: string
  note?: ReactNode
  children: ReactNode
}

export function Block({ eyebrow, title, note, children }: BlockProps) {
  return (
    <section className="flex flex-col gap-4">
      <Reveal className="flex flex-col gap-1">
        <span className="text-eyebrow font-semibold tracking-eyebrow text-primary uppercase">
          {eyebrow}
        </span>
        <div className="flex flex-wrap items-baseline justify-between gap-2">
          <h2 className="text-3xl">{title}</h2>
          {note && <span className="text-sm text-muted-foreground">{note}</span>}
        </div>
      </Reveal>
      {children}
    </section>
  )
}
