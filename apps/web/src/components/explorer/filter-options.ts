import { countryName, flagEmoji, placeLabel, tierLabel, trackLabel } from '@/lib/format'
import type { AIAgent, EcosystemTool, Integration, Project } from '@/lib/types'

import { countValues, type FilterKey, type Selection } from './filters'

export interface Option {
  value: string
  label: string
  count: number
  hint?: string
}

const FIXED: Record<'award' | 'tier' | 'track' | 'activity', [string, string][]> = {
  award: [
    ['first', placeLabel.first],
    ['runner-up', placeLabel['runner-up']],
  ],
  tier: [
    ['verified', tierLabel.verified],
    ['likely', tierLabel.likely],
  ],
  track: [
    ['genesis', trackLabel.genesis],
    ['scale', trackLabel.scale],
  ],
  activity: [
    ['contracts', 'Deployed contracts'],
    ['failed', 'Failed transactions'],
  ],
}

export function options(
  key: FilterKey,
  projects: Project[],
  integrations: Integration[],
  tools: EcosystemTool[],
  agents: AIAgent[],
  selection: Selection,
): Option[] {
  const counts = countValues(projects, selection, key)
  const chosen = new Set(selection[key])
  const labelled: [string, string, string?][] =
    key === 'award' || key === 'tier' || key === 'track' || key === 'activity'
      ? FIXED[key].map(([value, label]) => [value, label])
      : key === 'partner'
        ? integrations.map((item) => [item.slug, item.name, item.category])
        : key === 'tool'
          ? tools.map((item) => [item.slug, item.name])
          : key === 'agent'
            ? agents.map((item) => [item.slug, item.name])
            : [
                ...new Set(
                  projects.flatMap(
                    (project) => (key === 'language' ? project.language : project.country) ?? [],
                  ),
                ),
              ].map((value) => [
                value,
                key === 'country' ? `${flagEmoji(value)} ${countryName(value)}` : value,
              ])
  return labelled
    .map(([value, label, hint]) => ({ value, label, hint, count: counts.get(value) ?? 0 }))
    .filter((option) => option.count > 0 || chosen.has(option.value))
    .sort((a, b) => (key in FIXED ? 0 : b.count - a.count || a.label.localeCompare(b.label)))
}

export interface FilterGroup {
  key: FilterKey
  title: string
  clause: string
  lower?: boolean
  collapsible: boolean
  questions: string[]
}

export const GROUPS: FilterGroup[] = [
  {
    key: 'award',
    title: 'Awards',
    clause: 'awarded {label}',
    lower: true,
    collapsible: false,
    questions: [
      'What did the projects awarded {label} build?',
      'What do the {label} winners have in common?',
      'How did the {label} winners compare with everyone else on chain?',
      'Which Stellar tools and partners did the {label} winners use?',
    ],
  },
  {
    key: 'tier',
    title: 'Evidence',
    clause: 'marked {label}',
    lower: true,
    collapsible: false,
    questions: [
      'What are the projects with {label} evidence building?',
      'What separates the {label} projects from the rest?',
      'Which partners and tools show up most among the {label} projects?',
      'How many contracts did the {label} projects deploy?',
    ],
  },
  {
    key: 'track',
    title: 'Track',
    clause: 'on the {label} track',
    lower: true,
    collapsible: false,
    questions: [
      'What did the {label} projects build?',
      'How do the {label} projects compare with the other track on chain?',
      'Which {label} projects stand out, and why?',
      'What stack do the {label} projects use?',
    ],
  },
  {
    key: 'partner',
    title: 'Integrations',
    clause: 'integrating {label}',
    collapsible: true,
    questions: [
      'What did the teams using {label} build?',
      'How did these projects use {label}? Show the evidence.',
      'Which other partners and tools do they combine with {label}?',
      'Did the {label} projects deploy more contracts than the rest?',
    ],
  },
  {
    key: 'tool',
    title: 'Ecosystem tooling',
    clause: 'built with {label}',
    collapsible: false,
    questions: [
      'What did the teams using {label} build?',
      'How did these projects use {label}?',
      'Which partners do the {label} projects pair it with?',
      'How many of the {label} projects won an award?',
    ],
  },
  {
    key: 'agent',
    title: 'AI coding agents',
    clause: 'using {label}',
    collapsible: false,
    questions: [
      'What did the teams using {label} build?',
      'Which {label} projects deployed the most contracts?',
      'Did the {label} projects do better than the rest?',
      'How do we detect {label} in a repo, and what does that miss?',
    ],
  },
  {
    key: 'activity',
    title: 'On-chain activity',
    clause: 'with {label}',
    lower: true,
    collapsible: false,
    questions: [
      'What do the projects with {label} build?',
      'Which projects had the most {label}?',
      'Do projects with {label} win more often?',
    ],
  },
  {
    key: 'language',
    title: 'Language',
    clause: 'written in {label}',
    collapsible: true,
    questions: [
      'What did the {label} projects build?',
      'Which Stellar SDKs and tools do the {label} projects use?',
      'How do the {label} projects compare with the other languages?',
      'Which {label} projects deployed the most contracts?',
    ],
  },
  {
    key: 'country',
    title: 'Country',
    clause: 'from {label}',
    collapsible: true,
    questions: [
      'What did builders in {label} build?',
      'Which Stellar tools did the teams from {label} use?',
      'How many contracts did the projects from {label} deploy?',
      'Did any projects from {label} win an award?',
    ],
  },
]

export const VIEW_QUESTIONS = [
  'Summarize the projects in this view',
  'Which of these projects stand out, and why?',
  'What do these projects have in common?',
]

const SUGGESTION_LIMIT = 5

const FLAG = /^\p{Regional_Indicator}+\s*/u

export function joinLabels(labels: string[]) {
  const plain = labels.map((label) => label.replace(FLAG, ''))
  if (plain.length < 2) return plain.join('')
  return `${plain.slice(0, -1).join(', ')} or ${plain[plain.length - 1]}`
}

export interface SelectedGroup {
  key: FilterKey
  title: string
  clause: string
  lower: boolean
  labels: string[]
  questions: string[]
}

export function selectedGroups(
  selection: Selection,
  projects: Project[],
  integrations: Integration[],
  tools: EcosystemTool[],
  agents: AIAgent[],
): SelectedGroup[] {
  return GROUPS.filter(({ key }) => selection[key].length > 0).map(
    ({ key, title, clause, lower = false, questions }) => {
      const known = options(key, projects, integrations, tools, agents, selection)
      return {
        key,
        title,
        clause,
        lower,
        questions,
        labels: selection[key].map(
          (value) => known.find((option) => option.value === value)?.label ?? value,
        ),
      }
    },
  )
}

export function filterQuestions(groups: SelectedGroup[]) {
  const fill = (group: SelectedGroup, question: string) =>
    question.replaceAll('{label}', joinLabels(group.labels))
  const firsts = groups.map((group) => fill(group, group.questions[0]))
  const rest = groups.flatMap((group) => group.questions.slice(1).map((q) => fill(group, q)))
  const [summary, ...more] = VIEW_QUESTIONS
  const ordered =
    groups.length > 1 ? [summary, ...firsts, ...rest, ...more] : [...firsts, ...rest, summary]

  return [...new Set(ordered)].slice(0, SUGGESTION_LIMIT)
}
