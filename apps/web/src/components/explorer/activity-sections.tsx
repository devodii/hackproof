import { DataTable } from '@/components/data-table'
import { Section } from '@/components/section'
import type { Contract, FailedTx, WasmUpload } from '@/lib/types'

import { contractColumns, failedColumns, wasmColumns } from './columns'

interface ActivitySectionsProps {
  contracts: Contract[]
  wasmUploads: WasmUpload[]
  failedTxs: FailedTx[]
}

export function ActivitySections({ contracts, wasmUploads, failedTxs }: ActivitySectionsProps) {
  return (
    <>
      {contracts.length > 0 && (
        <Section value="contracts" title="Contracts" count={contracts.length}>
          <DataTable columns={contractColumns} rows={contracts} rowKey={(row) => row.contract_id} />
        </Section>
      )}
      {wasmUploads.length > 0 && (
        <Section value="wasm" title="Wasm uploads" count={wasmUploads.length}>
          <DataTable columns={wasmColumns} rows={wasmUploads} rowKey={(row) => row.tx_hash} />
        </Section>
      )}
      {failedTxs.length > 0 && (
        <Section value="failed" title="Failed transactions" count={failedTxs.length}>
          <DataTable columns={failedColumns} rows={failedTxs} rowKey={(row) => row.tx_hash} />
        </Section>
      )}
    </>
  )
}
