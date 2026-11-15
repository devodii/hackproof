import { ArrowLeftIcon } from 'lucide-react'
import { useMemo } from 'react'
import { Link, useLocation, useNavigate, useSearchParams } from 'react-router'

import { Button } from '@/components/ui/button'
import { useAgents, useIntegrations, useProjects, useTools } from '@/hooks/use-projects'
import { formatNumber } from '@/lib/format'

import { GROUPS, options } from './filter-options'
import { matches, readSelection } from './filters'

export function FilterHeading() {
  const [params] = useSearchParams()
  const location = useLocation()
  const navigate = useNavigate()
  const { data: projects = [] } = useProjects()
  const { data: integrations = [] } = useIntegrations()
  const { data: tools = [] } = useTools()
  const { data: agents = [] } = useAgents()
  const selection = useMemo(() => readSelection(params), [params])

  const groups = GROUPS.filter(({ key }) => selection[key].length > 0).map(({ key, title }) => {
    const known = options(key, projects, integrations, tools, agents, selection)
    return {
      key,
      title,
      labels: selection[key].map(
        (value) => known.find((option) => option.value === value)?.label ?? value,
      ),
    }
  })
  const count = projects.filter((project) => matches(project, selection)).length
  const canGoBack = location.key !== 'default'

  return (
    <header className="flex flex-col items-start gap-3">
      {canGoBack ? (
        <Button variant="ghost" size="sm" className="-ml-2.5" onClick={() => navigate(-1)}>
          <ArrowLeftIcon /> Back
        </Button>
      ) : (
        <Button variant="ghost" size="sm" className="-ml-2.5" render={<Link to="/" />}>
          <ArrowLeftIcon /> All projects
        </Button>
      )}
      <h1 className="font-heading text-4xl leading-tight text-balance sm:text-6xl">
        {groups.map((group, index) => (
          <span key={group.key}>
            {index > 0 && <span className="text-muted-foreground"> · </span>}
            <span className="text-muted-foreground">{group.title}: </span>
            {group.labels.join(', ')}
          </span>
        ))}
      </h1>
      <p className="text-muted-foreground">
        {formatNumber(count)} {count === 1 ? 'project matches' : 'projects match'}
      </p>
    </header>
  )
}
