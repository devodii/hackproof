import { useMemo } from 'react'
import { useSearchParams } from 'react-router'

import { useAgents, useIntegrations, useProjects, useTools } from '@/hooks/use-projects'

import { selectedGroups } from './filter-options'
import { readSelection } from './filters'

export function useSelectedGroups() {
  const [params] = useSearchParams()
  const { data: projects = [] } = useProjects()
  const { data: integrations = [] } = useIntegrations()
  const { data: tools = [] } = useTools()
  const { data: agents = [] } = useAgents()
  const selection = useMemo(() => readSelection(params), [params])

  return {
    selection,
    projects,
    groups: selectedGroups(selection, projects, integrations, tools, agents),
  }
}
