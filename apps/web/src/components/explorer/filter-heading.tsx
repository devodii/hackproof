import { ArrowLeftIcon } from 'lucide-react'
import { Link, useLocation, useNavigate } from 'react-router'

import { useChatPanel } from '@/components/chat/use-chat-panel'
import { Button } from '@/components/ui/button'
import { formatNumber } from '@/lib/format'

import { filterQuestions } from './filter-options'
import { matches } from './filters'
import { useSelectedGroups } from './use-selected-groups'

export function FilterHeading() {
  const location = useLocation()
  const navigate = useNavigate()
  const { startChat } = useChatPanel()
  const { selection, projects, groups } = useSelectedGroups()
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
      <div className="flex flex-wrap gap-2">
        {filterQuestions(groups).map((question) => (
          <Button
            key={question}
            variant="outline"
            size="sm"
            className="h-auto rounded-full px-3 py-1.5 text-left whitespace-normal"
            onClick={() => startChat(question)}
          >
            {question}
          </Button>
        ))}
      </div>
    </header>
  )
}
