import { SearchIcon } from 'lucide-react'
import { useState } from 'react'
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
