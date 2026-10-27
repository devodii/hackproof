import type { Column } from '@/components/data-table'
import { BuilderLink, ExternalId, ProjectLink } from '@/components/links'
import { Badge } from '@/components/ui/badge'
import {
  expertUrl,
  flagEmoji,
  formatBytes,
  formatDateTime,
  formatNumber,
  shortId,
} from '@/lib/format'
import type { Contract, FailedTx, Project, WasmUpload } from '@/lib/types'

const numeric = 'text-right tabular-nums'

export const projectColumns: Column<Project>[] = [
  {
    header: 'Project',
    cell: (row) => (
      <div className="flex flex-col gap-0.5">
        <span className="flex items-center gap-2">
          <ProjectLink projectId={row.project_id} />
          {row.country && <span title={row.country}>{flagEmoji(row.country)}</span>}
          {!row.full_name && <Badge variant="outline">unlinked</Badge>}
        </span>
        {row.description && (
          <span className="line-clamp-1 max-w-md text-xs text-muted-foreground">
            {row.description}
          </span>
        )}
      </div>
    ),
  },
  { header: 'Contracts', className: numeric, cell: (row) => formatNumber(row.contracts) },
  { header: 'Wasm', className: numeric, cell: (row) => formatNumber(row.wasm_uploads) },
  { header: 'Failed', className: numeric, cell: (row) => formatNumber(row.failed_txs) },
  { header: 'Last deploy', cell: (row) => formatDateTime(row.last_deployed_at) },
]

export const contractColumns: Column<Contract>[] = [
  {
    header: 'Contract',
    cell: (row) => (
      <ExternalId value={row.contract_id} href={expertUrl.contract(row.contract_id)} />
    ),
  },
  { header: 'Deployer', cell: (row) => <BuilderLink value={row.deployer} /> },
  {
    header: 'Project',
    cell: (row) => <ProjectLink projectId={row.project_id} />,
  },
  { header: 'Deployed', cell: (row) => formatDateTime(row.deployed_at) },
]

export const wasmColumns: Column<WasmUpload>[] = [
  {
    header: 'Wasm hash',
    cell: (row) => (
      <ExternalId value={row.wasm_hash} href={expertUrl.tx(row.tx_hash)} head={8} tail={6} />
    ),
  },
  { header: 'Uploader', cell: (row) => <BuilderLink value={row.uploader} /> },
  {
    header: 'Repo',
    cell: (row) =>
      row.full_name ? (
        <a
          href={`https://github.com/${row.full_name}`}
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
  { header: 'Source', cell: (row) => <BuilderLink value={row.source_account} /> },
  { header: 'Kind', cell: (row) => <Badge variant="secondary">{row.kind}</Badge> },
  {
    header: 'Result',
    cell: (row) => (
      <span className="font-mono text-xs" title={row.result_code}>
        {shortId(row.result_code.toLowerCase(), 28, 0)}
      </span>
    ),
  },
  { header: 'Time', cell: (row) => formatDateTime(row.created_at) },
]
