import { CheckIcon, ChevronsUpDownIcon, LayoutGridIcon } from 'lucide-react'
import { Link } from 'react-router'

import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { useHackathon } from '@/hooks/use-hackathon'
import { useHackathons } from '@/hooks/use-hackathons'
import { formatNumber } from '@/lib/format'
import { hackathonPath } from '@/lib/hackathon'

export function HackathonSwitcher() {
  const current = useHackathon()
  const { data = [] } = useHackathons()

  return (
    <DropdownMenu>
      <DropdownMenuTrigger
        translate="no"
        className="inline-flex min-w-0 items-center gap-1 rounded-md px-1.5 py-1 text-sm text-muted-foreground outline-none hover:bg-muted hover:text-foreground data-popup-open:bg-muted data-popup-open:text-foreground"
      >
        <span className="truncate">{current.name}</span>
        <ChevronsUpDownIcon className="size-3.5 shrink-0" />
      </DropdownMenuTrigger>
      <DropdownMenuContent align="start" className="min-w-96">
        <DropdownMenuGroup>
          <DropdownMenuLabel>Switch hackathon</DropdownMenuLabel>
          {data.map((item) => (
            <DropdownMenuItem
              key={item.slug}
              render={<Link to={hackathonPath(item.slug)} />}
              className="justify-between gap-6"
            >
              <span translate="no" className="flex items-center gap-2">
                {item.slug === current.slug ? (
                  <CheckIcon className="size-3.5" />
                ) : (
                  <span className="size-3.5" />
                )}
                {item.name}
              </span>
              <span className="text-xs whitespace-nowrap text-muted-foreground">
                {item.indexed ? `${formatNumber(item.projects)} projects` : 'Not indexed'}
              </span>
            </DropdownMenuItem>
          ))}
        </DropdownMenuGroup>
        <DropdownMenuSeparator />
        <DropdownMenuItem render={<Link to="/" />}>
          <LayoutGridIcon /> All hackathons
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
