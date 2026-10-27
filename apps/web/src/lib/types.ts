export interface Page<T> {
  items: T[]
  total: number
}

export interface HackWindow {
  start: string
  end: string
}

export interface Stats {
  projects: number
  linked_projects: number
  contracts: number
  builders: number
  countries: number
  wasm_uploads: number
  failed_txs: number
}

export interface Project {
  project_id: string
  full_name: string | null
  contracts: number
  builders: number
  wasm_uploads: number
  failed_txs: number
  first_deployed_at: string
  last_deployed_at: string
  description: string | null
  stars: number | null
  owner: string | null
  owner_avatar: string | null
  country: string | null
}

export interface Contract {
  contract_id: string
  deployer: string
  wasm_hash: string
  tx_hash: string
  ledger: number
  deployed_at: string
  project_id: string
}

export interface WasmUpload {
  wasm_hash: string
  uploader: string
  tx_hash: string
  size: number
  source_repo: string | null
  full_name: string | null
  contracts: number
  uploaded_at: string
}

export interface FailedTx {
  tx_hash: string
  source_account: string
  kind: string
  result_code: string
  ledger: number
  created_at: string
}

export interface ProjectDetail {
  project: Project
  contracts: Contract[]
  wasm_uploads: WasmUpload[]
  failed_txs: FailedTx[]
}

export interface Builder {
  address: string
  projects: Project[]
  contracts: Contract[]
  wasm_uploads: WasmUpload[]
  failed_txs: FailedTx[]
}

export interface Challenge {
  message: string
}

export interface Proof {
  proof_id: string
  address: string
  claimed_at: string
  projects: number
  contracts: number
  wasm_uploads: number
  failed_txs: number
  first_activity: string
  last_activity: string
  window_start: string
  window_end: string
}
