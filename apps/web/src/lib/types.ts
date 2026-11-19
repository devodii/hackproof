import type { Project } from '@/lib/api-schema'

export type {
  AiAgent,
  Adopter,
  Builder,
  CaptureCount,
  CheckCount,
  Contract,
  ContractSnapshot,
  ContractState,
  Contributor,
  Count,
  CountryCount,
  DependencyFingerprint,
  EcosystemTool,
  FailedTx,
  Integration,
  IntegrationDepth,
  IntegrationDetail,
  IntegrationProfile,
  IntegrationUse,
  Link,
  Person,
  PersonProject,
  ProfileCheck,
  ProfileContractUse,
  ProfileSignal,
  ProjectDetail,
  Reading,
  SignalCount,
  Stats,
  TimelinePoint,
  WasmUpload,
  Wrapped,
  WrappedBuilder,
} from '@/lib/api-schema'
export type { Project }

export interface Page<T> {
  items: T[]
  total: number
}

export interface HackWindow {
  start: string
  end: string
}

export type Footprint = Project['footprint']
export type Track = NonNullable<Project['track']>
export type Place = NonNullable<Project['award']>
export type Tier = Project['tier']
export type Fact = number | string | null
