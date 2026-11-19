import { Link } from 'react-router'

import { CheckStatus } from '@/components/integration/check-status'
import { DataTable, type Column } from '@/components/data-table'
import { TierBadge } from '@/components/tier-badge'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Badge } from '@/components/ui/badge'
import { projectName } from '@/lib/format'
import type { Adopter } from '@/lib/types'

const columns: Column<Adopter>[] = [
  {
    header: 'Project',
    cell: (row) => (
      <Link
        to={`/project/${row.project_id}`}
        className="inline-flex items-center gap-2 font-medium hover:underline"
      >
        <Avatar size="sm">
          {row.owner_avatar && <AvatarImage src={row.owner_avatar} alt="" />}
          <AvatarFallback>{row.owner.slice(0, 2).toUpperCase()}</AvatarFallback>
        </Avatar>
        {projectName(row.project_id)}
      </Link>
    ),
  },
  { header: 'Tier', cell: (row) => <TierBadge tier={row.tier} /> },
  {
    header: 'Contracts',
    cell: (row) => (
      <span className="flex flex-wrap gap-1.5">
        {row.profile.contracts.map((contract) => (
          <Badge key={contract.id} variant="outline">
            {contract.name} · {contract.network}
          </Badge>
        ))}
      </span>
    ),
  },
  {
    header: 'Asks for',
    cell: (row) => (
      <span className="font-mono text-xs">
        {Object.values(row.profile.captures).flat().join(', ') || '-'}
      </span>
    ),
  },
  {
    header: 'Checks',
    cell: (row) => (
      <span className="flex gap-1.5">
        {row.profile.checks.map((check) => (
          <CheckStatus key={check.slug} check={check} />
        ))}
      </span>
    ),
  },
]

export function AdoptersTable({ adopters }: { adopters: Adopter[] }) {
  return (
    <DataTable
      columns={columns}
      rows={adopters}
      rowKey={(row) => row.project_id}
      paginate={false}
    />
  )
}
