import { Link } from '@/components/hackathon/hackathon-link'

import { CheckStatus } from '@/components/integration/check-status'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import type { IntegrationDepth } from '@/lib/types'

export function DepthCard({ depth }: { depth: IntegrationDepth }) {
  const { profile } = depth

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between gap-3">
          <span className="font-heading text-2xl font-normal">{depth.name} in depth</span>
          <Link
            to={`/integration/${depth.slug}`}
            className="text-sm font-normal text-muted-foreground hover:text-foreground hover:underline"
          >
            All {depth.name} projects
          </Link>
        </CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col gap-4">
        {profile.contracts.length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            {profile.contracts.map((contract) => (
              <a key={contract.id} href={contract.explorer_url} target="_blank" rel="noreferrer">
                <Badge variant="outline">
                  {contract.name} · {contract.network}
                </Badge>
              </a>
            ))}
          </div>
        )}
        {Object.entries(profile.captures).map(([name, values]) => (
          <div key={name} className="flex flex-wrap items-center gap-1.5">
            <span className="text-sm text-muted-foreground">{name}</span>
            {values.map((value) => (
              <Badge key={value} variant="secondary" className="font-mono">
                {value}
              </Badge>
            ))}
          </div>
        ))}
        {profile.signals.length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            {profile.signals.map((signal) => (
              <Badge key={signal.slug} variant="secondary">
                {signal.label}
              </Badge>
            ))}
          </div>
        )}
        {profile.checks.length > 0 && (
          <ul className="flex flex-col gap-1.5 text-sm">
            {profile.checks.map((check) => (
              <li key={check.slug} className="flex items-center gap-2">
                <CheckStatus check={check} />
                {check.label}
              </li>
            ))}
          </ul>
        )}
      </CardContent>
    </Card>
  )
}
