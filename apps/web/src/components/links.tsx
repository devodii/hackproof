import { ExternalLinkIcon } from 'lucide-react'
import { Link } from 'react-router'

import { formatNumber, projectName, shortId } from '@/lib/format'
import { expertUrl } from '@/lib/links'

const styles = 'font-mono text-xs hover:underline'
const iconStyles = 'size-3 text-muted-foreground'

interface ExternalIdProps {
  value: string
  href: string
  head?: number
  tail?: number
}

export function ExternalId({ value, href, head, tail }: ExternalIdProps) {
  return (
    <a
      href={href}
      target="_blank"
      rel="noreferrer"
      className={`${styles} inline-flex items-center gap-1`}
    >
      {shortId(value, head, tail)}
      <ExternalLinkIcon className={iconStyles} />
    </a>
  )
}

export function AccountLink({ address }: { address: string }) {
  return (
    <span className="inline-flex items-center gap-1">
      <Link to={`/builder/${address}`} className={styles}>
        {shortId(address)}
      </Link>
      <a
        href={expertUrl.account(address)}
        target="_blank"
        rel="noreferrer"
        aria-label="View account on Stellar Expert"
      >
        <ExternalLinkIcon className={iconStyles} />
      </a>
    </span>
  )
}

export function LedgerLink({ sequence }: { sequence: number }) {
  return (
    <a
      href={expertUrl.ledger(sequence)}
      target="_blank"
      rel="noreferrer"
      className={`${styles} inline-flex items-center gap-1 tabular-nums`}
    >
      {formatNumber(sequence)}
      <ExternalLinkIcon className={iconStyles} />
    </a>
  )
}

export function ProjectLink({ projectId }: { projectId: string }) {
  return (
    <Link to={`/project/${projectId}`} className="font-medium hover:underline">
      {projectName(projectId)}
    </Link>
  )
}

export function EvidenceSubject({ kind, subject }: { kind: string; subject: string }) {
  if (kind === 'contract') {
    return <ExternalId value={subject} href={expertUrl.contract(subject)} head={8} tail={6} />
  }
  if (kind === 'account') {
    return <ExternalId value={subject} href={expertUrl.account(subject)} head={8} tail={6} />
  }
  if (kind === 'asset') {
    return <ExternalId value={subject} href={expertUrl.asset(subject)} head={14} tail={6} />
  }
  return (
    <Link to={`/?tab=wasm&q=${subject}`} className={styles}>
      {shortId(subject, 8, 6)}
    </Link>
  )
}
