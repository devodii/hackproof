import { ExternalLinkIcon } from 'lucide-react'
import { Link } from 'react-router'

import { projectName, shortId } from '@/lib/format'

interface LinkProps {
  value: string
  head?: number
  tail?: number
}

const styles = 'font-mono text-xs hover:underline'

export function ExternalId({ value, href, head, tail }: LinkProps & { href: string }) {
  return (
    <a
      href={href}
      target="_blank"
      rel="noreferrer"
      className={`${styles} inline-flex items-center gap-1`}
    >
      {shortId(value, head, tail)}
      <ExternalLinkIcon className="size-3 text-muted-foreground" />
    </a>
  )
}

export function BuilderLink({ value }: LinkProps) {
  return (
    <Link to={`/builder/${value}`} className={styles}>
      {shortId(value)}
    </Link>
  )
}

export function ProjectLink({ projectId }: { projectId: string }) {
  return (
    <Link to={`/project/${projectId}`} className="font-medium hover:underline">
      {projectName(projectId)}
    </Link>
  )
}
