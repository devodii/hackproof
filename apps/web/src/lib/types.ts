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
  agents: string[]
}

export interface AiAgent {
  slug: string
  name: string
  site: string
  projects: number
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
  deep: boolean
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
  method: string
  evidence: string
  path: string
}

export interface ProfileContractUse {
  slug: string
  id: string
  name: string
  network: string
  kind: string
  explorer_url: string
  attributes: Record<string, string>
}

export interface ProfileSignal {
  slug: string
  group: string
  label: string
}

export interface ProfileCheck {
  slug: string
  label: string
  status: 'pass' | 'warn' | 'fail'
}

export interface IntegrationProfile {
  contracts: ProfileContractUse[]
  signals: ProfileSignal[]
  captures: Record<string, string[]>
  checks: ProfileCheck[]
}

export interface IntegrationDepth {
  slug: string
  name: string
  profile: IntegrationProfile
}

export type Fact = number | string | null

export interface ContractSnapshot {
  facts: Record<string, Fact>
  items: string[]
  deadlines: Record<string, number>
}

export interface ContractState {
  slug: string
  id: string
  name: string
  network: string
  kind: string
  attributes: Record<string, string>
  explorer_url: string
  snapshot: ContractSnapshot | null
  observed_at: string | null
  projects: number
  expired: string[]
}

export interface Adopter {
  project_id: string
  full_name: string
  url: string
  owner: string
  owner_avatar: string | null
  tier: Tier
  language: string | null
  profile: IntegrationProfile
}

export interface SignalCount {
  slug: string
  label: string
  group: string
  projects: number
}

export interface CheckCount {
  slug: string
  label: string
  severity: 'warn' | 'fail'
  passing: number
  failing: number
}

export interface CaptureCount {
  value: string
  projects: number
  offered_by: string[]
  expired_on: string[]
}

export interface IntegrationDetail {
  slug: string
  name: string
  category: string
  site: string
  contracts: ContractState[]
  adopters: Adopter[]
  of_projects: number
  signals: SignalCount[]
  checks: CheckCount[]
  captures: Record<string, CaptureCount[]>
  overlap: { total: number; matched: number; by_contract: Record<string, number> } | null
  live: string[]
}

export interface Reading {
  contract: string
  subject: string
  value: string | null
  timestamp: number | null
  age_seconds: number | null
  stale: boolean | null
  facts: Record<string, Fact>
}

export interface ProjectDetail {
  project: Project
  links: Link[]
  integration_uses: IntegrationUse[]
  integration_depths: IntegrationDepth[]
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

export interface PersonProject {
  project: Project
  contributions: number
}

export interface Person {
  login: string
  url: string
  avatar_url: string | null
  country: string | null
  contributions: number
  projects: PersonProject[]
}

export interface WrappedBuilder {
  login: string
  avatar_url: string | null
  projects: number
  contributions: number
  project_names: string[]
}

export interface Wrapped {
  builders: number
  accounts_funded: number
  deployers: number
  operations: number
  largest_wasm_contracts: number
  operations_by_type: Count[]
  team_sizes: Count[]
  multi_team_builders: WrappedBuilder[]
  top_builders: WrappedBuilder[]
}
