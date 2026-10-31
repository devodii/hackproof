import { SearchIcon } from 'lucide-react'
import { useEffect, useRef, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useSearchParams } from 'react-router'

import { Input } from '@/components/ui/input'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { useDebouncedValue } from '@/hooks/use-debounced-value'
import type { Contract, FailedTx, WasmUpload } from '@/lib/types'

import { contractColumns, failedColumns, wasmColumns } from './columns'
import { ProjectExplorer } from './project-explorer'
import { ResourceTable } from './resource-table'

export function Explorer() {
  const [params, setParams] = useSearchParams()
  const [input, setInput] = useState(params.get('q') ?? '')
  const search = useDebouncedValue(input.trim())
  const top = useRef<HTMLDivElement>(null)
  const awards = params.has('award')
  const { t } = useTranslation()

  useEffect(() => {
    if (awards) top.current?.scrollIntoView({ behavior: 'smooth' })
  }, [awards])

  const setParam = (key: string, value: string) =>
    setParams((previous) => {
      const next = new URLSearchParams(previous)
      next.set(key, value)
      return next
    })

  return (
    <Tabs
      value={params.get('tab') ?? 'projects'}
      onValueChange={(tab) => setParam('tab', tab)}
      className="w-full gap-4"
    >
      <div
        ref={top}
        className="flex scroll-mt-4 flex-col gap-3 sm:flex-row sm:items-center sm:justify-between"
      >
        <TabsList>
          <TabsTrigger value="projects">{t('explorer.tabs.projects')}</TabsTrigger>
          <TabsTrigger value="contracts">{t('explorer.tabs.contracts')}</TabsTrigger>
          <TabsTrigger value="wasm">{t('explorer.tabs.wasm')}</TabsTrigger>
          <TabsTrigger value="failed">{t('explorer.tabs.failed')}</TabsTrigger>
        </TabsList>
        <div className="relative w-full sm:max-w-xs">
          <SearchIcon className="absolute top-1/2 left-2.5 size-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            value={input}
            onChange={(event) => setInput(event.target.value)}
            placeholder={t('explorer.searchPlaceholder')}
            className="pl-8"
          />
        </div>
      </div>
      <TabsContent value="projects">
        <ProjectExplorer search={search.toLowerCase()} />
      </TabsContent>
      <TabsContent value="contracts">
        <ResourceTable<Contract>
          key={search}
          resource="contracts"
          search={search}
          columns={contractColumns}
          rowKey={(row) => row.contract_id}
          empty={t('explorer.noContracts')}
        />
      </TabsContent>
      <TabsContent value="wasm">
        <ResourceTable<WasmUpload>
          key={search}
          resource="wasm"
          search={search}
          columns={wasmColumns}
          rowKey={(row) => row.tx_hash}
          empty={t('explorer.noWasm')}
        />
      </TabsContent>
      <TabsContent value="failed">
        <ResourceTable<FailedTx>
          key={search}
          resource="failed"
          search={search}
          columns={failedColumns}
          rowKey={(row) => row.tx_hash}
          empty={t('explorer.noFailed')}
        />
      </TabsContent>
    </Tabs>
  )
}
