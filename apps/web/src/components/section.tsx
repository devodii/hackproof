import type { ReactNode } from 'react'

import { AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion'
import { Badge } from '@/components/ui/badge'
import { formatNumber } from '@/lib/format'

interface SectionProps {
  value: string
  title: string
  count?: number
  children: ReactNode
}

export function Section({ value, title, count, children }: SectionProps) {
  return (
    <AccordionItem value={value}>
      <AccordionTrigger className="items-center py-4">
        <span className="flex items-center gap-3">
          <span className="font-heading text-2xl font-normal">{title}</span>
          {count !== undefined && <Badge variant="outline">{formatNumber(count)}</Badge>}
        </span>
      </AccordionTrigger>
      <AccordionContent className="pt-1 pb-4">{children}</AccordionContent>
    </AccordionItem>
  )
}
