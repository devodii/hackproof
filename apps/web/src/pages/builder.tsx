import { ExternalLinkIcon } from 'lucide-react'
import { useParams } from 'react-router'

import { ClientTable } from '@/components/client-table'
import { ActivityTabs } from '@/components/explorer/activity-tabs'
import { projectColumns } from '@/components/explorer/columns'
import { DetailError, DetailSkeleton } from '@/components/query-state'
import { useBuilder } from '@/hooks/use-builder'
import { expertUrl } from '@/lib/links'

export function BuilderPage() {
  const address = useParams().address ?? ''
  const { data, isPending, error } = useBuilder(address)

  if (isPending) return <DetailSkeleton />
  if (error) return <DetailError error={error} subject="builder" />

  return (
    <div className="flex flex-col gap-8">
      <header className="flex flex-col gap-2">
        <h1 className="text-5xl">Builder</h1>
        <a
          href={expertUrl.account(data.address)}
          target="_blank"
          rel="noreferrer"
          className="inline-flex items-center gap-1 font-mono text-sm break-all text-muted-foreground hover:text-foreground"
        >
          {data.address}
          <ExternalLinkIcon className="size-3.5 shrink-0" />
        </a>
      </header>
      <section className="flex flex-col gap-3">
        <h2 className="text-lg font-medium">Projects</h2>
        <ClientTable
          columns={projectColumns}
          rows={data.projects}
          rowKey={(row) => row.project_id}
          empty="No projects."
        />
      </section>
      <ActivityTabs
        contracts={data.contracts}
        wasmUploads={data.wasm_uploads}
        failedTxs={data.failed_txs}
      />
    </div>
  )
}
