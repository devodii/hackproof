import { SearchIcon } from 'lucide-react'
import { useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router'

import { Input } from '@/components/ui/input'
import { Switch } from '@/components/ui/switch'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { useDebouncedValue } from '@/hooks/use-debounced-value'
import { STRICT_TIERS } from '@/lib/format'
import type { Contract, FailedTx, Project, WasmUpload } from '@/lib/types'

import { contractColumns, failedColumns, projectColumns, wasmColumns } from './columns'
import { ProjectGrid } from './project-grid'
import { ResourceTable } from './resource-table'

export function Explorer() {
  const [params, setParams] = useSearchParams()
  const [input, setInput] = useState(params.get('q') ?? '')
  const [strict, setStrict] = useState(true)
  const navigate = useNavigate()
  const view = params.get('view') === 'table' ? 'table' : 'cards'
  const search = useDebouncedValue(input.trim())

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
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <TabsList>
          <TabsTrigger value="projects">Projects</TabsTrigger>
          <TabsTrigger value="contracts">Contracts</TabsTrigger>
          <TabsTrigger value="wasm">Wasm</TabsTrigger>
          <TabsTrigger value="failed">Failed</TabsTrigger>
        </TabsList>
        <div className="relative w-full sm:max-w-xs">
          <SearchIcon className="absolute top-1/2 left-2.5 size-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            value={input}
            onChange={(event) => setInput(event.target.value)}
            placeholder="Search address, hash or repo"
            className="pl-8"
          />
        </div>
      </div>
      <TabsContent value="projects" className="flex flex-col gap-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <label className="flex items-center gap-2 text-sm text-muted-foreground">
            <Switch checked={strict} onCheckedChange={setStrict} />
            Strict: verified on-chain, declared or likely HackMeridian projects only
          </label>
          <Tabs value={view} onValueChange={(next) => setParam('view', next)}>
            <TabsList>
              <TabsTrigger value="cards">Cards</TabsTrigger>
              <TabsTrigger value="table">Table</TabsTrigger>
            </TabsList>
          </Tabs>
        </div>
        {view === 'cards' ? (
          <ProjectGrid
            key={`${search}:${strict}`}
            search={search}
            tiers={strict ? STRICT_TIERS : undefined}
          />
        ) : (
          <ResourceTable<Project>
            key={`${search}:${strict}`}
            tiers={strict ? STRICT_TIERS : undefined}
            resource="projects"
            search={search}
            columns={projectColumns}
            rowKey={(row) => row.project_id}
            empty="No projects match."
            onRowClick={(row) => navigate(`/project/${row.project_id}`)}
          />
        )}
      </TabsContent>
      <TabsContent value="contracts">
        <ResourceTable<Contract>
          key={search}
          resource="contracts"
          search={search}
          columns={contractColumns}
          rowKey={(row) => row.contract_id}
          empty="No contracts match."
        />
      </TabsContent>
      <TabsContent value="wasm">
        <ResourceTable<WasmUpload>
          key={search}
          resource="wasm"
          search={search}
          columns={wasmColumns}
          rowKey={(row) => row.tx_hash}
          empty="No wasm uploads match."
        />
      </TabsContent>
      <TabsContent value="failed">
        <ResourceTable<FailedTx>
          key={search}
          resource="failed"
          search={search}
          columns={failedColumns}
          rowKey={(row) => row.tx_hash}
          empty="No failed transactions match."
        />
      </TabsContent>
    </Tabs>
  )
}
