import { ExternalLinkIcon } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { useNavigate, useParams } from 'react-router'

import { DataTable } from '@/components/data-table'
import { ActivitySections } from '@/components/explorer/activity-sections'
import { projectColumns } from '@/components/explorer/columns'
import { BuilderSkeleton } from '@/components/page-skeletons'
import { DetailError } from '@/components/query-state'
import { Section } from '@/components/section'
import { Accordion } from '@/components/ui/accordion'
import { useBuilder } from '@/hooks/use-builder'
import { expertUrl } from '@/lib/links'

export function BuilderPage() {
  const address = useParams().address ?? ''
  const navigate = useNavigate()
  const { data, isPending, error } = useBuilder(address)
  const { t } = useTranslation()

  if (isPending) return <BuilderSkeleton />
  if (error) return <DetailError error={error} subject={t('builder.title').toLowerCase()} />

  return (
    <div className="flex flex-col gap-8">
      <header className="flex flex-col gap-2">
        <h1 className="text-5xl">{t('builder.title')}</h1>
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
      <Accordion multiple defaultValue={['projects']}>
        {data.projects.length > 0 && (
          <Section value="projects" title={t('builder.projects')} count={data.projects.length}>
            <DataTable
              columns={projectColumns}
              rows={data.projects}
              rowKey={(row) => row.project_id}
              onRowClick={(row) => navigate(`/project/${row.project_id}`)}
            />
          </Section>
        )}
        <ActivitySections
          contracts={data.contracts}
          wasmUploads={data.wasm_uploads}
          failedTxs={data.failed_txs}
        />
      </Accordion>
    </div>
  )
}
