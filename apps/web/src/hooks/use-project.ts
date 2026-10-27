import { useQuery } from '@tanstack/react-query'

import { apiGet } from '@/lib/api'
import type { ProjectDetail } from '@/lib/types'

export function useProject(projectId: string) {
  return useQuery({
    queryKey: ['project', projectId],
    queryFn: () => apiGet<ProjectDetail>(`/projects/${projectId}`),
  })
}
