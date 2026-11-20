import { motion } from 'motion/react'
import { useState } from 'react'
import { useSearchParams } from 'react-router'

import { Link } from '@/components/hackathon/hackathon-link'

import { EventLogo } from '@/components/brand/event-logo'
import { Backdrop } from '@/components/wrapped/backdrop'
import { BuilderAvatars } from '@/components/wrapped/builder-avatars'
import { Figure } from '@/components/wrapped/figure'
import { LensList, type LensRow } from '@/components/wrapped/lens-list'
import { RankedBars } from '@/components/wrapped/ranked-bars'
import { type Segment, SegmentedBar } from '@/components/wrapped/segmented-bar'
import { Stage } from '@/components/wrapped/stage'
import { TeamBars } from '@/components/wrapped/team-bars'
import { Tile } from '@/components/wrapped/tile'
import { TimelineChart } from '@/components/wrapped/timeline-chart'
import { StillContext, useStill } from '@/components/wrapped/use-still'
import { Waffle } from '@/components/wrapped/waffle'
import { useHackWindow } from '@/hooks/use-hack-window'
import { useMediaQuery } from '@/hooks/use-media-query'
import { useAgents, useIntegrations, useProjects, useTools } from '@/hooks/use-projects'
import { useStats } from '@/hooks/use-stats'
import { useTimeline } from '@/hooks/use-timeline'
import { useWrapped } from '@/hooks/use-wrapped'
import { useHackathon } from '@/hooks/use-hackathon'
import { formatHour, formatNumber, humanize, tierLabel } from '@/lib/format'
import type {
  AIAgent,
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
  explorerPath,
  matchesLens,
  parseLens,
  POSTER_MEDIA,
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
  agents: AIAgent[]
  window: HackWindow
}

interface SectionProps {
  data: PosterData
  lens: Lens | null
  onPreview: (lens: Lens | null) => void
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

function Header({ window }: { window: HackWindow }) {
  const still = useStill()
  const hackathon = useHackathon()

  return (
    <motion.header
      initial={still ? false : { opacity: 0, y: -14 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.7, ease: EASE_OUT }}
      className="flex flex-col gap-1 lg:flex-row lg:items-end lg:justify-between"
    >
      <div className="flex items-center gap-4">
        <EventLogo className="h-7 w-auto sm:h-9" />
        <h1 className="font-heading text-headline">
          <span className="sr-only">{hackathon.name} </span>
          <span className="text-brand italic">Wrapped</span>
        </h1>
      </div>
      <p className="pb-1 text-sm text-muted-foreground">{windowLabel(window)}</p>
    </motion.header>
  )
}

function languageCounts(projects: Project[]): Segment[] {
  const counts = new Map<string, number>()
  projects.forEach((project) => {
    const language = project.language ?? 'Other'
    counts.set(language, (counts.get(language) ?? 0) + 1)
  })
  const sorted = [...counts].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))
  const rest = sorted.slice(LANGUAGES_SHOWN).reduce((sum, [, value]) => sum + value, 0)
  return [
    ...sorted.slice(0, LANGUAGES_SHOWN).map(([label, value]) => ({
      label,
      value,
      lens: { kind: 'language' as const, value: label },
    })),
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

function Hero({ data, lens, onPreview }: SectionProps) {
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
          className="font-heading text-display text-brand"
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
              <b className="font-semibold text-brand">{summary.matched}</b> of {projects.length}{' '}
              projects: {summary.name}
            </span>
          ) : (
            tiers.map(({ tier, swatch }) => (
              <Link
                key={tier}
                to={explorerPath({ kind: 'tier', value: tier })}
                onMouseEnter={() => onPreview({ kind: 'tier', value: tier })}
                onMouseLeave={() => onPreview(null)}
                className="flex items-center gap-2 hover:text-foreground"
              >
                <i className={`size-2.5 rounded-sm ${swatch}`} />
                {tier === 'verified' ? stats.verified_projects : stats.likely_projects}{' '}
                {tierLabel[tier].toLowerCase()}
              </Link>
            ))
          )}
        </div>
        <div className="mt-3">
          <SegmentedBar
            data={languageCounts(projects)}
            active={lens}
            onPreview={onPreview}
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
  const hours = data.timeline.length
  const figures = [
    ['contracts deployed', data.stats.contracts],
    ['deployers', data.wrapped.deployers],
    ['accounts funded', data.wrapped.accounts_funded],
    ['operations', data.wrapped.operations],
  ]

  return (
    <Tile title={`The ${hours} hours on chain`} note="contracts deployed per hour" delay={0.25}>
      <div className="mb-1 flex flex-wrap gap-x-10 gap-y-4">
        {figures.map(([label, value], index) => (
          <div key={label}>
            <div className="font-heading text-figure">
              <Figure value={Number(value)} delay={0.7 + index * 0.1} />
            </div>
            <div className="mt-1 text-xs text-muted-foreground">{label}</div>
          </div>
        ))}
        <div className="flex w-full flex-wrap gap-2 text-xs lg:ml-auto lg:w-auto lg:flex-col lg:items-end lg:justify-center lg:gap-1">
          <span className="rounded-full border border-tile-border bg-track px-2.5 py-1">
            <b className="text-brand">{formatNumber(peak.contracts)}</b> in one hour at{' '}
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
    <Tile
      title="What the chain did"
      note="top operations"
      delay={0.4}
      grow={5}
      className="lg:basis-0"
    >
      <RankedBars data={rows} className="h-chart-md lg:h-auto lg:min-h-0 lg:flex-1" />
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
    <Tile title="Builders" note="people per repo" delay={0.5} grow={4} className="lg:basis-0">
      <TeamBars data={teams} className="h-chart-sm lg:h-auto lg:min-h-chart-sm lg:flex-1" />
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
        {hidden > 0 && (
          <Link
            to="/contributors"
            aria-label={`See all ${wrapped.multi_team_builders.length} builders on 2 or more teams`}
            className="text-xs text-muted-foreground underline-offset-4 hover:text-brand hover:underline"
          >
            +{hidden}
          </Link>
        )}
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

function Agents({ data, lens, onPreview }: SectionProps) {
  const rows = ranked(data.agents, 'agent', AGENT_ROWS)

  if (rows.length === 0) return null

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
        onPreview={onPreview}
        delay={0.9}
      />
    </Tile>
  )
}

function Tooling({ data, lens, onPreview }: SectionProps) {
  const rows = ranked(data.tools, 'tool', data.tools.length)

  if (rows.length === 0) return null

  return (
    <Tile title="Stellar tooling" note="projects using it" delay={0.5} grow={rows.length}>
      <LensList
        rows={rows}
        total={data.projects.length}
        active={lens}
        onPreview={onPreview}
        delay={1}
      />
    </Tile>
  )
}

function BuiltWith({ data, lens, onPreview }: SectionProps) {
  const rows = ranked(data.integrations, 'integration', INTEGRATION_ROWS)

  if (rows.length === 0) return null

  return (
    <Tile title="Built with" note="partner integrations" delay={0.65} grow={rows.length}>
      <LensList
        rows={rows}
        total={data.projects.length}
        active={lens}
        onPreview={onPreview}
        delay={1.1}
      />
    </Tile>
  )
}

function Footer() {
  return (
    <p className="flex flex-col gap-1 text-eyebrow text-muted-foreground lg:flex-row lg:justify-between">
      <span>
        Rebuilt from the Stellar testnet and GitHub. Every project links to its on chain evidence.
      </span>
      <span>hackproof-six.vercel.app</span>
    </p>
  )
}

function usePosterData(): { data: PosterData | undefined; failed: boolean } {
  const queries = {
    wrapped: useWrapped(),
    stats: useStats(),
    timeline: useTimeline(),
    projects: useProjects(),
    integrations: useIntegrations(),
    tools: useTools(),
    agents: useAgents(),
    window: useHackWindow(),
  }
  const failed = Object.values(queries).some((query) => query.isError)
  const { wrapped, stats, timeline, projects, integrations, tools, agents, window } =
    Object.fromEntries(Object.entries(queries).map(([key, query]) => [key, query.data])) as {
      [K in keyof typeof queries]: (typeof queries)[K]['data']
    }

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
    return { data: undefined, failed }
  }
  return {
    data: { wrapped, stats, timeline, projects, integrations, tools, agents, window },
    failed,
  }
}

function Notice({ failed, className }: { failed: boolean; className: string }) {
  return (
    <div className={`relative grid place-items-center text-muted-foreground ${className}`}>
      {failed ? 'Could not load the numbers. Try again in a moment.' : 'Counting…'}
    </div>
  )
}

function Poster({ data, lens, onPreview }: SectionProps) {
  return (
    <div className="relative flex h-full flex-col gap-3.5 px-9 pt-7 pb-5">
      <Header window={data.window} />
      <div className="poster-grid min-h-0 flex-1 gap-3.5">
        <Hero data={data} lens={lens} onPreview={onPreview} />
        <div className="flex min-h-0 flex-col gap-3.5">
          <Chain data={data} />
          <div className="flex min-h-0 flex-1 gap-3.5">
            <Operations wrapped={data.wrapped} />
            <Builders wrapped={data.wrapped} />
          </div>
        </div>
        <div className="flex min-h-0 flex-col gap-3.5">
          <Agents data={data} lens={lens} onPreview={onPreview} />
          <Tooling data={data} lens={lens} onPreview={onPreview} />
          <BuiltWith data={data} lens={lens} onPreview={onPreview} />
        </div>
      </div>
      <Footer />
    </div>
  )
}

function Feed({ data, lens, onPreview }: SectionProps) {
  return (
    <div className="relative flex flex-col gap-3.5 px-4 py-6">
      <Header window={data.window} />
      <Hero data={data} lens={lens} onPreview={onPreview} />
      <Chain data={data} />
      <Operations wrapped={data.wrapped} />
      <Builders wrapped={data.wrapped} />
      <Agents data={data} lens={lens} onPreview={onPreview} />
      <Tooling data={data} lens={lens} onPreview={onPreview} />
      <BuiltWith data={data} lens={lens} onPreview={onPreview} />
      <Footer />
    </div>
  )
}

export function WrappedPage() {
  const [params] = useSearchParams()
  const [preview, setPreview] = useState<Lens | null>(null)
  const { data, failed } = usePosterData()
  const isPoster = useMediaQuery(POSTER_MEDIA)
  const still = params.has('still')
  const lens = preview ?? parseLens(params.get('lens'))

  if (isPoster) {
    return (
      <Stage still={still}>
        <Backdrop />
        {data ? (
          <Poster data={data} lens={lens} onPreview={setPreview} />
        ) : (
          <Notice failed={failed} className="h-full" />
        )}
      </Stage>
    )
  }

  return (
    <StillContext value={still}>
      <div className="dark relative min-h-svh overflow-hidden bg-background text-foreground">
        <Backdrop />
        {data ? (
          <Feed data={data} lens={lens} onPreview={setPreview} />
        ) : (
          <Notice failed={failed} className="min-h-svh" />
        )}
      </div>
    </StillContext>
  )
}
