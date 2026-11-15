import { motion } from 'motion/react'
import { useSearchParams } from 'react-router'

import { BuilderAvatars } from '@/components/wrapped/builder-avatars'
import { Figure } from '@/components/wrapped/figure'
import { LensList, type LensRow } from '@/components/wrapped/lens-list'
import { RankedBars } from '@/components/wrapped/ranked-bars'
import { SegmentedBar } from '@/components/wrapped/segmented-bar'
import { Stage } from '@/components/wrapped/stage'
import { TeamBars } from '@/components/wrapped/team-bars'
import { Tile } from '@/components/wrapped/tile'
import { TimelineChart } from '@/components/wrapped/timeline-chart'
import { useStill } from '@/components/wrapped/use-still'
import { Waffle } from '@/components/wrapped/waffle'
import { useHackWindow } from '@/hooks/use-hack-window'
import { useAgents, useIntegrations, useProjects, useTools } from '@/hooks/use-projects'
import { useStats } from '@/hooks/use-stats'
import { useTimeline } from '@/hooks/use-timeline'
import { useWrapped } from '@/hooks/use-wrapped'
import { formatHour, formatNumber, humanize, tierLabel } from '@/lib/format'
import type {
  AiAgent,
  EcosystemTool,
  HackWindow,
  Integration,
  Project,
  Stats,
  TimelinePoint,
  Wrapped,
} from '@/lib/types'
import {
  EASE_OUT,
  formatLens,
  isSameLens,
  matchesLens,
  parseLens,
  timelineHighlights,
  type Lens,
} from '@/lib/wrapped'

const WAFFLE_COLUMNS = 15
const LANGUAGES_SHOWN = 4
const AGENT_ROWS = 6
const INTEGRATION_ROWS = 5
const SOLO_TEAM = '1'
const LARGEST_TEAM = '5'
const TOP_BUILDERS = 5
const MULTI_TEAM_BUILDERS = 8

interface PosterData {
  wrapped: Wrapped
  stats: Stats
  timeline: TimelinePoint[]
  projects: Project[]
  integrations: Integration[]
  tools: EcosystemTool[]
  agents: AiAgent[]
  window: HackWindow
}

interface SectionProps {
  data: PosterData
  lens: Lens | null
  onSelect: (lens: Lens) => void
}

const day = new Intl.DateTimeFormat('en', { month: 'short', day: 'numeric', timeZone: 'UTC' })

function windowLabel({ start, end }: HackWindow) {
  const hours = Math.round((new Date(end).getTime() - new Date(start).getTime()) / 3_600_000)
  return `${day.format(new Date(start))} to ${day.format(new Date(end))} · ${hours} hours · Stellar testnet`
}

function ranked<T extends { slug: string; name: string; projects: number }>(
  items: T[],
  kind: Lens['kind'],
  limit: number,
): LensRow[] {
  return items
    .filter((item) => item.projects > 0)
    .sort((a, b) => b.projects - a.projects || a.name.localeCompare(b.name))
    .slice(0, limit)
    .map((item) => ({ label: item.name, value: item.projects, lens: { kind, value: item.slug } }))
}

function Backdrop() {
  return (
    <div aria-hidden className="pointer-events-none absolute inset-0">
      <div className="absolute -top-60 -left-40 size-glow rounded-full bg-glow-secondary blur-glow" />
      <div className="absolute -right-48 -bottom-72 size-glow-lg rounded-full bg-glow-primary blur-glow-lg" />
      <div className="poster-dots absolute inset-0" />
    </div>
  )
}

function Header({ window }: { window: HackWindow }) {
  const still = useStill()

  return (
    <motion.header
      initial={still ? false : { opacity: 0, y: -14 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.7, ease: EASE_OUT }}
      className="flex items-end justify-between"
    >
      <h1 className="font-heading text-headline">
        HackMeridian 2026 <span className="text-primary italic">Wrapped</span>
      </h1>
      <p className="pb-1 text-sm text-muted-foreground">{windowLabel(window)}</p>
    </motion.header>
  )
}

function languageCounts(projects: Project[]) {
  const counts = new Map<string, number>()
  projects.forEach((project) => {
    const language = project.language ?? 'Other'
    counts.set(language, (counts.get(language) ?? 0) + 1)
  })
  const sorted = [...counts].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))
  const rest = sorted.slice(LANGUAGES_SHOWN).reduce((sum, [, value]) => sum + value, 0)
  return [
    ...sorted.slice(0, LANGUAGES_SHOWN).map(([label, value]) => ({ label, value })),
    ...(rest ? [{ label: 'Other', value: rest }] : []),
  ]
}

function lensSummary(lens: Lens, data: PosterData) {
  const matched = data.projects.filter((project) => matchesLens(project, lens)).length
  const names: Record<Lens['kind'], string | undefined> = {
    tier: tierLabel[lens.value as keyof typeof tierLabel],
    agent: data.agents.find((item) => item.slug === lens.value)?.name,
    tool: data.tools.find((item) => item.slug === lens.value)?.name,
    integration: data.integrations.find((item) => item.slug === lens.value)?.name,
    language: lens.value,
  }
  return { matched, name: names[lens.kind] ?? lens.value }
}

function Hero({ data, lens, onSelect }: SectionProps) {
  const { stats, projects } = data
  const commits = projects.reduce((sum, project) => sum + (project.window_commits ?? 0), 0)
  const summary = lens && lensSummary(lens, data)
  const tiers: { tier: 'verified' | 'likely'; swatch: string }[] = [
    { tier: 'verified', swatch: 'bg-primary' },
    { tier: 'likely', swatch: 'bg-secondary' },
  ]

  return (
    <Tile title="The field" delay={0.1} className="justify-between">
      <div className="flex items-end gap-3">
        <Figure
          value={stats.projects}
          delay={0.5}
          className="font-heading text-display text-primary"
        />
        <p className="pb-2 text-sm leading-tight text-foreground/80">
          projects
          <br />
          shipped
        </p>
      </div>
      <div>
        <Waffle projects={projects} lens={lens} columns={WAFFLE_COLUMNS} delay={0.7} />
        <div className="mt-3 flex min-h-6 items-center gap-5 text-xs text-foreground/80">
          {summary ? (
            <span>
              <b className="font-semibold text-primary">{summary.matched}</b> of {projects.length}{' '}
              projects: {summary.name}
            </span>
          ) : (
            tiers.map(({ tier, swatch }) => (
              <button
                key={tier}
                type="button"
                onClick={() => onSelect({ kind: 'tier', value: tier })}
                className="flex items-center gap-2 hover:text-foreground"
              >
                <i className={`size-2.5 rounded-sm ${swatch}`} />
                {tier === 'verified' ? stats.verified_projects : stats.likely_projects}{' '}
                {tierLabel[tier].toLowerCase()}
              </button>
            ))
          )}
        </div>
        <div className="mt-3">
          <SegmentedBar
            data={languageCounts(projects)}
            active={lens}
            onSelect={onSelect}
            delay={1}
          />
        </div>
      </div>
      <dl className="grid grid-cols-3 gap-3 border-t border-tile-border pt-4">
        {[
          ['GitHub builders', data.wrapped.builders],
          ['Commits', commits],
          ['Countries', stats.countries],
        ].map(([label, value], index) => (
          <div key={label}>
            <dt className="text-eyebrow text-muted-foreground">{label}</dt>
            <dd className="font-heading text-figure">
              <Figure value={Number(value)} delay={1.1 + index * 0.1} />
            </dd>
          </div>
        ))}
      </dl>
    </Tile>
  )
}

function Chain({ data }: { data: PosterData }) {
  const { peak, rush, rushTotal } = timelineHighlights(data.timeline)
  const figures = [
    ['contracts deployed', data.stats.contracts],
    ['deployers', data.wrapped.deployers],
    ['accounts funded', data.wrapped.accounts_funded],
    ['operations', data.wrapped.operations],
  ]

  return (
    <Tile title="The 27 hours on chain" note="contracts deployed per hour" delay={0.25}>
      <div className="mb-1 flex gap-10">
        {figures.map(([label, value], index) => (
          <div key={label}>
            <div className="font-heading text-figure">
              <Figure value={Number(value)} delay={0.7 + index * 0.1} />
            </div>
            <div className="mt-1 text-xs text-muted-foreground">{label}</div>
          </div>
        ))}
        <div className="ml-auto flex flex-col items-end justify-center gap-1 text-xs">
          <span className="rounded-full border border-tile-border bg-track px-2.5 py-1">
            <b className="text-primary">{formatNumber(peak.contracts)}</b> in one hour at{' '}
            {formatHour(peak.hour)} UTC
          </span>
          <span className="rounded-full border border-tile-border bg-track px-2.5 py-1">
            <b className="text-secondary">{formatNumber(rushTotal)}</b> in the last {rush.length}h
          </span>
        </div>
      </div>
      <TimelineChart data={data.timeline} peak={peak} rush={rush} className="h-chart-lg" />
    </Tile>
  )
}

function Operations({ wrapped }: { wrapped: Wrapped }) {
  const rows = wrapped.operations_by_type.map((row) => ({ ...row, label: humanize(row.label) }))

  return (
    <Tile title="What the chain did" note="top operations" delay={0.4} grow={5} className="basis-0">
      <RankedBars data={rows} className="min-h-0 flex-1" />
    </Tile>
  )
}

function Builders({ wrapped }: { wrapped: Wrapped }) {
  const teams = wrapped.team_sizes.map((row) => ({
    ...row,
    label:
      row.label === SOLO_TEAM ? 'Solo' : row.label === LARGEST_TEAM ? `${row.label}+` : row.label,
  }))
  const hidden = wrapped.multi_team_builders.length - MULTI_TEAM_BUILDERS

  return (
    <Tile title="Builders" note="people per repo" delay={0.5} grow={4} className="basis-0">
      <TeamBars data={teams} className="min-h-chart-sm flex-1" />
      <div className="mt-3 flex items-center gap-2 text-xs text-foreground/80">
        <b className="font-heading text-stat text-secondary">
          {wrapped.multi_team_builders.length}
        </b>
        shipped with 2+ teams
      </div>
      <div className="mt-2 flex items-center gap-2">
        <BuilderAvatars
          builders={wrapped.multi_team_builders.slice(0, MULTI_TEAM_BUILDERS)}
          size="sm"
          delay={1}
        />
        {hidden > 0 && <span className="text-xs text-muted-foreground">+{hidden}</span>}
      </div>
      <p className="mt-3 text-eyebrow tracking-eyebrow text-muted-foreground uppercase">
        Most commits
      </p>
      <div className="mt-2">
        <BuilderAvatars
          builders={wrapped.top_builders.slice(0, TOP_BUILDERS)}
          size="lg"
          delay={1.2}
        />
      </div>
    </Tile>
  )
}

function Agents({ data, lens, onSelect }: SectionProps) {
  const rows = ranked(data.agents, 'agent', AGENT_ROWS)

  return (
    <Tile
      title="AI in the repos"
      note="projects with its config or commits"
      delay={0.35}
      grow={rows.length}
    >
      <LensList
        rows={rows}
        total={data.projects.length}
        active={lens}
        onSelect={onSelect}
        delay={0.9}
      />
    </Tile>
  )
}

function Tooling({ data, lens, onSelect }: SectionProps) {
  const rows = ranked(data.tools, 'tool', data.tools.length)

  return (
    <Tile title="Stellar tooling" note="projects using it" delay={0.5} grow={rows.length}>
      <LensList
        rows={rows}
        total={data.projects.length}
        active={lens}
        onSelect={onSelect}
        delay={1}
      />
    </Tile>
  )
}

function BuiltWith({ data, lens, onSelect }: SectionProps) {
  const rows = ranked(data.integrations, 'integration', INTEGRATION_ROWS)

  return (
    <Tile title="Built with" note="partner integrations" delay={0.65} grow={rows.length}>
      <LensList
        rows={rows}
        total={data.projects.length}
        active={lens}
        onSelect={onSelect}
        delay={1.1}
      />
    </Tile>
  )
}

function Footer() {
  return (
    <p className="flex justify-between text-eyebrow text-muted-foreground">
      <span>
        Rebuilt from the Stellar testnet and GitHub. Every project links to its on chain evidence.
      </span>
      <span>hackproof-six.vercel.app</span>
    </p>
  )
}

function usePosterData(): PosterData | undefined {
  const { data: wrapped } = useWrapped()
  const { data: stats } = useStats()
  const { data: timeline } = useTimeline()
  const { data: projects } = useProjects()
  const { data: integrations } = useIntegrations()
  const { data: tools } = useTools()
  const { data: agents } = useAgents()
  const { data: window } = useHackWindow()

  if (
    !wrapped ||
    !stats ||
    !timeline ||
    !projects ||
    !integrations ||
    !tools ||
    !agents ||
    !window
  ) {
    return undefined
  }
  return { wrapped, stats, timeline, projects, integrations, tools, agents, window }
}

export function WrappedPage() {
  const [params, setParams] = useSearchParams()
  const data = usePosterData()
  const lens = parseLens(params.get('lens'))

  const select = (next: Lens) => {
    const updated = new URLSearchParams(params)
    if (isSameLens(lens, next)) updated.delete('lens')
    else updated.set('lens', formatLens(next))
    setParams(updated, { replace: true })
  }

  return (
    <Stage still={params.has('still')}>
      <Backdrop />
      {data ? (
        <div className="relative flex h-full flex-col gap-3.5 px-9 pt-7 pb-5">
          <Header window={data.window} />
          <div className="poster-grid min-h-0 flex-1 gap-3.5">
            <Hero data={data} lens={lens} onSelect={select} />
            <div className="flex min-h-0 flex-col gap-3.5">
              <Chain data={data} />
              <div className="flex min-h-0 flex-1 gap-3.5">
                <Operations wrapped={data.wrapped} />
                <Builders wrapped={data.wrapped} />
              </div>
            </div>
            <div className="flex min-h-0 flex-col gap-3.5">
              <Agents data={data} lens={lens} onSelect={select} />
              <Tooling data={data} lens={lens} onSelect={select} />
              <BuiltWith data={data} lens={lens} onSelect={select} />
            </div>
          </div>
          <Footer />
        </div>
      ) : (
        <div className="relative grid h-full place-items-center text-muted-foreground">
          Counting…
        </div>
      )}
    </Stage>
  )
}
