import { ChevronDownIcon } from 'lucide-react'
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
import { useIntegrations, useTools } from '@/hooks/use-projects'
import { formatNumber } from '@/lib/format'

interface Entry {
  slug: string
  name: string
  projects: number
}

function Group({ title, entries }: { title: string; entries: Entry[] }) {
  if (entries.length === 0) return null

  return (
    <DropdownMenuGroup>
      <DropdownMenuLabel>{title}</DropdownMenuLabel>
      {entries.map((entry) => (
        <DropdownMenuItem
          key={entry.slug}
          render={<Link to={`/integration/${entry.slug}`} />}
          className="justify-between gap-6"
        >
          {entry.name}
          <span className="text-xs text-muted-foreground">
            {formatNumber(entry.projects)} projects
          </span>
        </DropdownMenuItem>
      ))}
    </DropdownMenuGroup>
  )
}

export function IntegrationsMenu() {
  const { data: partners = [] } = useIntegrations()
  const { data: tools = [] } = useTools()
  const deepPartners = partners.filter((item) => item.deep)
  const deepTools = tools.filter((item) => item.deep)

  if (deepPartners.length + deepTools.length === 0) return null

  return (
    <DropdownMenu>
      <DropdownMenuTrigger className="inline-flex items-center gap-1 text-sm text-muted-foreground outline-none hover:text-foreground">
        Integrations <ChevronDownIcon className="size-3.5" />
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="min-w-64">
        <Group title="Partners" entries={deepPartners} />
        {deepPartners.length > 0 && deepTools.length > 0 && <DropdownMenuSeparator />}
        <Group title="Tools" entries={deepTools} />
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
