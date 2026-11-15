import { ArrowLeftIcon } from 'lucide-react'
import { Link, useLocation, useNavigate } from 'react-router'

import { useChatPanel } from '@/components/chat/use-chat-panel'
import { Button } from '@/components/ui/button'
import { EVENT_NAME } from '@/lib/config'
import { formatNumber } from '@/lib/format'

import { filterQuestions, joinLabels, type SelectedGroup } from './filter-options'
import { matches } from './filters'
import { useSelectedGroups } from './use-selected-groups'

function lowerFirst(label: string) {
  return label.charAt(0).toLowerCase() + label.slice(1)
}

function clauseOf(group: SelectedGroup) {
  const [before, after = ''] = group.clause.split('{label}')
  const labels = group.lower ? group.labels.map(lowerFirst) : group.labels
  return { key: group.key, before, label: joinLabels(labels), after }
}

function separator(index: number, total: number) {
  if (index === 0) return ' '
  return index === total - 1 ? ' and ' : ', '
}

export function FilterHeading() {
  const location = useLocation()
  const navigate = useNavigate()
  const { startChat } = useChatPanel()
  const { selection, projects, groups } = useSelectedGroups()
  const count = projects.filter((project) => matches(project, selection)).length
  const canGoBack = location.key !== 'default'
  const clauses = groups.map(clauseOf)

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
        <span className="text-muted-foreground">{EVENT_NAME} projects</span>
        {clauses.map((clause, index) => (
          <span key={clause.key}>
            <span className="text-muted-foreground">
              {separator(index, clauses.length)}
              {clause.before}
            </span>
            {clause.label}
            <span className="text-muted-foreground">{clause.after}</span>
          </span>
        ))}
      </h1>
      <p className="text-muted-foreground">
        {formatNumber(count)} of {formatNumber(projects.length)} projects match
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
