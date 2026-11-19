import { AlertTriangleIcon, CircleCheckIcon, CircleXIcon } from 'lucide-react'

import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip'
import type { ProfileCheck } from '@/lib/types'
import { cn } from '@/lib/utils'

const icons = {
  pass: { Icon: CircleCheckIcon, className: 'text-ok' },
  warn: { Icon: AlertTriangleIcon, className: 'text-warn' },
  fail: { Icon: CircleXIcon, className: 'text-destructive' },
}

export function CheckStatus({ check }: { check: ProfileCheck }) {
  const { Icon, className } = icons[check.status]

  return (
    <Tooltip>
      <TooltipTrigger render={<span aria-label={check.label} />}>
        <Icon className={cn('size-4', className)} />
      </TooltipTrigger>
      <TooltipContent>{check.label}</TooltipContent>
    </Tooltip>
  )
}

export function SeverityIcon({ severity }: { severity: 'warn' | 'fail' }) {
  const { Icon, className } = icons[severity]

  return <Icon className={cn('size-4 shrink-0', className)} />
}
