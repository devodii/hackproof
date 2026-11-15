export interface Page<T> {
  items: T[]
  total: number
}

export interface HackWindow {
  start: string
  end: string
}

export type Footprint = 'contracts' | 'classic' | 'github'
export type Track = 'genesis' | 'scale'
export type Place = 'first' | 'runner-up'
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
  award: Place | null
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
  track: Track | null
  integrations: string[]
  tools: string[]
}

export interface EcosystemTool {
  slug: string
  name: string
  site: string
  projects: number
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
  tool_uses: IntegrationUse[]
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

export interface Count {
  label: string
  value: number
}

export interface Wrapped {
  window_start: string
  window_end: string
  projects: number
  verified_projects: number
  builders: number
  commits: number
  countries: number
  contracts: number
  deployers: number
  accounts_funded: number
  operations: number
  failed_txs: number
  largest_wasm_contracts: number
  readable_projects: number
  new_projects: number
  multi_team_builders: number
  ai_agent_projects: number
  timeline: TimelinePoint[]
  operations_by_type: Count[]
  languages: Count[]
  stack: Count[]
  partners: Count[]
  team_sizes: Count[]
  tracks: Count[]
}
