import { ExternalLinkIcon } from 'lucide-react'

import type { Column } from '@/components/data-table'
import {
  AccountLink,
  EvidenceSubject,
  ExternalId,
  LedgerLink,
  ProjectLink,
} from '@/components/links'
import { Badge } from '@/components/ui/badge'
import {
  flagEmoji,
  footprintLabel,
  tierLabel,
  formatBytes,
  formatDateTime,
  formatLastActivity,
  formatNumber,
  shortId,
} from '@/lib/format'
import { expertUrl, githubUrl } from '@/lib/links'
import type { Contract, FailedTx, Link, Project, WasmUpload } from '@/lib/types'

const numeric = 'text-right tabular-nums'

export const projectColumns: Column<Project>[] = [
  {
    header: 'Project',
    cell: (row) => (
      <div className="flex flex-col gap-0.5">
        <span className="flex items-center gap-2">
          <ProjectLink projectId={row.project_id} />
          {row.country && <span title={row.country}>{flagEmoji(row.country)}</span>}
          {!row.full_name && <Badge variant="outline">no repo</Badge>}
        </span>
        {row.description && (
          <span className="line-clamp-1 max-w-md text-xs text-muted-foreground">
            {row.description}
          </span>
        )}
      </div>
    ),
  },
  {
    header: 'Evidence',
    cell: (row) => (
      <Badge variant={row.tier === 'verified' ? 'default' : 'secondary'}>
        {tierLabel[row.tier]}
      </Badge>
    ),
  },
  {
    header: 'Footprint',
    cell: (row) => <Badge variant="secondary">{footprintLabel[row.footprint]}</Badge>,
  },
  { header: 'Contracts', className: numeric, cell: (row) => formatNumber(row.contracts) },
  { header: 'Classic ops', className: numeric, cell: (row) => formatNumber(row.classic_ops) },
  { header: 'Wasm', className: numeric, cell: (row) => formatNumber(row.wasm_uploads) },
  { header: 'Failed', className: numeric, cell: (row) => formatNumber(row.failed_txs) },
  { header: 'Last activity', cell: (row) => formatLastActivity(row.last_activity) },
]

export const contractColumns: Column<Contract>[] = [
  {
    header: 'Contract',
    cell: (row) => (
      <ExternalId value={row.contract_id} href={expertUrl.contract(row.contract_id)} />
    ),
  },
  { header: 'Deployer', cell: (row) => <AccountLink address={row.deployer} /> },
  {
    header: 'Project',
    cell: (row) => <ProjectLink projectId={row.project_id} />,
  },
  { header: 'Ledger', cell: (row) => <LedgerLink sequence={row.ledger} /> },
  { header: 'Deployed', cell: (row) => formatDateTime(row.deployed_at) },
]

export const wasmColumns: Column<WasmUpload>[] = [
  {
    header: 'Wasm hash',
    cell: (row) => (
      <ExternalId value={row.wasm_hash} href={expertUrl.tx(row.tx_hash)} head={8} tail={6} />
    ),
  },
  { header: 'Uploader', cell: (row) => <AccountLink address={row.uploader} /> },
  {
    header: 'Repo',
    cell: (row) =>
      row.full_name ? (
        <a
          href={githubUrl.repo(row.full_name)}
          target="_blank"
          rel="noreferrer"
          className="text-xs hover:underline"
        >
          {row.full_name}
        </a>
      ) : (
        <span className="text-muted-foreground">none</span>
      ),
  },
  { header: 'Size', className: numeric, cell: (row) => formatBytes(row.size) },
  { header: 'Contracts', className: numeric, cell: (row) => formatNumber(row.contracts) },
  { header: 'Uploaded', cell: (row) => formatDateTime(row.uploaded_at) },
]

export const failedColumns: Column<FailedTx>[] = [
  {
    header: 'Tx',
    cell: (row) => <ExternalId value={row.tx_hash} href={expertUrl.tx(row.tx_hash)} />,
  },
  { header: 'Source', cell: (row) => <AccountLink address={row.source_account} /> },
  { header: 'Kind', cell: (row) => <Badge variant="secondary">{row.kind}</Badge> },
  {
    header: 'Result',
    cell: (row) => (
      <span className="font-mono text-xs" title={row.result_code}>
        {shortId(row.result_code.toLowerCase(), 28, 0)}
      </span>
    ),
  },
  { header: 'Ledger', cell: (row) => <LedgerLink sequence={row.ledger} /> },
  { header: 'Time', cell: (row) => formatDateTime(row.created_at) },
]

export function linkColumns(fullName: string): Column<Link>[] {
  return [
    { header: 'Kind', cell: (row) => <Badge variant="outline">{row.subject_kind}</Badge> },
    {
      header: 'Matched',
      cell: (row) => <EvidenceSubject kind={row.subject_kind} subject={row.subject} />,
    },
    { header: 'Method', cell: (row) => <Badge variant="secondary">{row.method}</Badge> },
    {
      header: 'Found in',
      cell: (row) =>
        row.path ? (
          <a
            href={githubUrl.file(fullName, row.path)}
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-1 font-mono text-xs hover:underline"
          >
            {shortId(row.path, 24, 12)}
            <ExternalLinkIcon className="size-3 text-muted-foreground" />
          </a>
        ) : (
          <span className="text-xs text-muted-foreground">on-chain metadata</span>
        ),
    },
  ]
}
