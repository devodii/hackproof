import type { Stats, Tier } from '@/lib/types'

export interface StatDefinition {
  key: keyof Stats
  label: string
  meaning: string
  counted: string
}

export const STAT_DEFINITIONS: StatDefinition[] = [
  {
    key: 'projects',
    label: 'HackMeridian projects',
    meaning:
      'GitHub repos we treat as HackMeridian submissions. This is a reconstruction, not an official total: the real submission list is private.',
    counted: 'Repos in the verified, declared and likely tiers added together.',
  },
  {
    key: 'verified_projects',
    label: 'Verified on-chain',
    meaning:
      'Repos tied to testnet activity by an exact match, such as a deployed contract id, a wasm hash or a deploy account found in the repo.',
    counted:
      'At least one exact match, and the matched account was active inside the 27 hour window.',
  },
  {
    key: 'declared_projects',
    label: 'Declared',
    meaning: 'Repos that say they belong to HackMeridian, with work done during the event.',
    counted: 'The readme or a topic names HackMeridian, and at least one commit inside the window.',
  },
  {
    key: 'likely_projects',
    label: 'Likely',
    meaning:
      'Repos that look like hackathon builds from their history, but say nothing about it. A signal, not proof.',
    counted:
      'A Stellar dependency and commits in the window, and the repo was created during the hack or added its Stellar dependency during it.',
  },
  {
    key: 'possible_projects',
    label: 'Possible',
    meaning:
      'Stellar repos with some activity that weekend and no other evidence. Hidden by default because many are ordinary Stellar development.',
    counted: 'A Stellar dependency and at least 3 commits in the window.',
  },
  {
    key: 'unattributed_accounts',
    label: 'Accounts with no repo',
    meaning:
      'Stellar accounts that deployed or issued assets during the window where we found no repo. Some are bots, some shipped outside GitHub.',
    counted:
      'Accounts that deployed a contract, uploaded wasm or issued an asset in the window and are not linked to any repo.',
  },
  {
    key: 'contracts',
    label: 'Contracts deployed',
    meaning: 'Every Soroban contract deployed on testnet during the event, from any account.',
    counted:
      'Deploy operations between 09:00 UTC on 25 Oct and 12:00 UTC on 26 Oct. Not limited to the projects above.',
  },
  {
    key: 'builders',
    label: 'Deploy accounts',
    meaning: 'Distinct Stellar accounts that put code on testnet during the event.',
    counted: 'Accounts that deployed a contract or uploaded wasm inside the window.',
  },
  {
    key: 'contributors',
    label: 'Contributors',
    meaning: 'People who committed to the strict projects.',
    counted:
      'Distinct GitHub users in the contributor lists of the strict projects. Bots are excluded.',
  },
  {
    key: 'countries',
    label: 'Countries',
    meaning:
      'Countries represented by project owners and contributors. A floor, because most GitHub users list no location.',
    counted: 'Distinct countries parsed from public GitHub profile locations.',
  },
  {
    key: 'wasm_uploads',
    label: 'Wasm uploads',
    meaning: 'Contract code uploaded to testnet before any contract is created from it.',
    counted: 'Upload operations inside the window.',
  },
  {
    key: 'failed_txs',
    label: 'Failed transactions',
    meaning:
      'Soroban transactions that failed during the event: contract panics, fee estimation errors and resource limits.',
    counted: 'Failed invoke, deploy and upload transactions inside the window.',
  },
]

export const TIER_DEFINITIONS: { tier: Tier; label: string; rule: string; strict: boolean }[] = [
  {
    tier: 'verified',
    label: 'Verified on-chain',
    rule: 'An exact repo to chain match, with chain activity inside the window.',
    strict: true,
  },
  {
    tier: 'declared',
    label: 'Declared',
    rule: 'The readme or a topic names HackMeridian, with commits inside the window.',
    strict: true,
  },
  {
    tier: 'likely',
    label: 'Likely',
    rule: 'Stellar dependency and window commits, created or Stellar added during the window.',
    strict: true,
  },
  {
    tier: 'possible',
    label: 'Possible',
    rule: 'Stellar dependency and at least 3 window commits, nothing else.',
    strict: false,
  },
]

export const LIMITS = [
  'Private repos, and teams that never committed a deploy key or contract id, cannot be linked.',
  'Only GitHub is searched. Teams that shipped on other hosts are not in the data yet.',
  'Countries come from public GitHub locations, so the count is a floor.',
  'The official submission list is not public, so no percentage of the true total is claimed.',
]

export const DOWNLOADS = [
  { label: 'Projects (JSON)', href: '/data/hackmeridian-2026/projects.json' },
  { label: 'Projects (YAML)', href: '/data/hackmeridian-2026/projects.yml' },
  { label: 'Schema (JSON Schema)', href: '/schema/hackathon-export-1.0.json' },
  { label: 'Schema (YAML)', href: '/schema/hackathon-export-1.0.yml' },
]
