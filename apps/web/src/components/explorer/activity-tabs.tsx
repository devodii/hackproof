import { ClientTable } from '@/components/client-table'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import type { Contract, FailedTx, WasmUpload } from '@/lib/types'

import { contractColumns, failedColumns, wasmColumns } from './columns'

interface ActivityTabsProps {
  contracts: Contract[]
  wasmUploads: WasmUpload[]
  failedTxs: FailedTx[]
}

export function ActivityTabs({ contracts, wasmUploads, failedTxs }: ActivityTabsProps) {
  return (
    <Tabs defaultValue="contracts" className="w-full gap-4">
      <TabsList>
        <TabsTrigger value="contracts">Contracts ({contracts.length})</TabsTrigger>
        <TabsTrigger value="wasm">Wasm ({wasmUploads.length})</TabsTrigger>
        <TabsTrigger value="failed">Failed ({failedTxs.length})</TabsTrigger>
      </TabsList>
      <TabsContent value="contracts">
        <ClientTable
          columns={contractColumns}
          rows={contracts}
          rowKey={(row) => row.contract_id}
          empty="No contracts deployed."
        />
      </TabsContent>
      <TabsContent value="wasm">
        <ClientTable
          columns={wasmColumns}
          rows={wasmUploads}
          rowKey={(row) => row.tx_hash}
          empty="No wasm uploaded."
        />
      </TabsContent>
      <TabsContent value="failed">
        <ClientTable
          columns={failedColumns}
          rows={failedTxs}
          rowKey={(row) => row.tx_hash}
          empty="No failed transactions."
        />
      </TabsContent>
    </Tabs>
  )
}
