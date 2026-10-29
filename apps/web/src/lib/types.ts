export interface Page<T> {
  items: T[]
  total: number
}

export interface HackWindow {
  start: string
  end: string
}

export type Footprint = 'contracts' | 'classic' | 'github'
export type Tier = 'verified' | 'likely' | 'possible' | 'unattributed'

export interface Stats {
  projects: number
  verified_projects: number
  likely_projects: number
  possible_projects: number
  unattributed_accounts: number
  contracts: number
  builders: number
  contributors: number
  countries: number
  wasm_uploads: number
  failed_txs: number
}

export interface DependencyFingerprint {
  ecosystems: string[]
  packages: Record<string, string | null>
}

export interface Project {
  project_id: string
  full_name: string | null
  url: string | null
  footprint: Footprint
  tier: Tier
  contracts: number
  classic_ops: number
  assets: number
  builders: number
  wasm_uploads: number
  failed_txs: number
  first_activity: string | null
  last_activity: string | null
  description: string | null
  homepage: string | null
  stars: number | null
  forks: number | null
  language: string | null
  license: string | null
  owner: string | null
  owner_avatar: string | null
  country: string | null
  dependencies: DependencyFingerprint | null
  window_commits: number | null
  total_commits: number | null
  stellar_added_in_window: boolean | null
  created_at: string | null
  topics: string[] | null
  track: 'genesis' | 'scale' | null
  integrations: string[]
}

export interface Integration {
  slug: string
  name: string
  category: string
  site: string
  projects: number
}

export interface Contributor {
  login: string
  url: string
  avatar_url: string | null
  contributions: number
  country: string | null
}

export interface Link {
  subject_kind: string
  subject: string
  method: string
  path: string | null
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

export interface IntegrationUse {
  slug: string
  name: string
  method: 'package' | 'endpoint'
  evidence: string
  path: string
}

export interface ProjectDetail {
  project: Project
  links: Link[]
  integration_uses: IntegrationUse[]
  contributors: Contributor[]
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

export interface TimelinePoint {
  hour: string
  contracts: number
}

export interface CountryCount {
  country: string
  contributors: number
}
