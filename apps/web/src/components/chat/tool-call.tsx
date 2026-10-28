import { type DynamicToolUIPart, getToolName, type ToolUIPart } from 'ai'
import { CheckIcon, TriangleAlertIcon } from 'lucide-react'

import { Spinner } from '@/components/spinner'
import { formatNumber, shortId } from '@/lib/format'

const LABELS: Record<string, { running: string; done: string }> = {
  query_projects: { running: 'Searching projects', done: 'Searched projects' },
  query_contracts: { running: 'Looking up contracts', done: 'Looked up contracts' },
  query_wasm: { running: 'Looking up wasm uploads', done: 'Looked up wasm uploads' },
  query_failed: { running: 'Checking failed transactions', done: 'Checked failed transactions' },
  summarize_projects: { running: 'Summarizing the projects', done: 'Summarized the projects' },
  web_search: { running: 'Searching the web', done: 'Searched the web' },
  get_project: { running: 'Loading the project', done: 'Loaded the project' },
  get_builder: { running: 'Loading the builder', done: 'Loaded the builder' },
  get_stats: { running: 'Reading the headline numbers', done: 'Read the headline numbers' },
  get_timeline: { running: 'Reading the hourly timeline', done: 'Read the hourly timeline' },
  get_countries: {
    running: 'Counting contributors by country',
    done: 'Counted contributors by country',
  },
}

function compact(value: string) {
  return /\s/.test(value) ? value : shortId(value, 10, 6)
}

function filters(input: unknown) {
  if (!input || typeof input !== 'object') return null
  const entries = Object.entries(input).filter(
    ([key, value]) => value !== null && value !== undefined && key !== 'limit',
  )
  if (entries.length === 0) return null
  return entries
    .map(
      ([key, value]) =>
        `${key}: ${Array.isArray(value) ? value.join(', ') : compact(String(value))}`,
    )
    .join(' · ')
}

function summary(output: unknown) {
  if (Array.isArray(output)) return `${output.length} sources`
  if (!output || typeof output !== 'object' || !('items' in output) || !('total' in output)) {
    return null
  }
  const { items, total } = output as { items: unknown[]; total: number }
  return `${formatNumber(items.length)} of ${formatNumber(total)}`
}

export function ToolCall({ part }: { part: ToolUIPart | DynamicToolUIPart }) {
  const name = getToolName(part)
  const label = LABELS[name] ?? { running: `Running ${name}`, done: `Ran ${name}` }
  const running = part.state === 'input-streaming' || part.state === 'input-available'
  const failed = part.state === 'output-error'
  const detail = failed
    ? 'failed'
    : running
      ? filters(part.input)
      : [summary(part.output), filters(part.input)].filter(Boolean).join(' · ')

  return (
    <div
      className="flex w-fit max-w-full items-center gap-2 rounded-full border bg-muted/50 py-1 pr-3 pl-2 text-xs text-muted-foreground"
      role="status"
    >
      {running ? (
        <Spinner size={16} />
      ) : failed ? (
        <TriangleAlertIcon className="size-4 text-destructive" />
      ) : (
        <CheckIcon className="size-4 text-foreground" />
      )}
      <span className="truncate">
        <span className="text-foreground">{running ? `${label.running}…` : label.done}</span>
        {detail && <span> · {detail}</span>}
      </span>
    </div>
  )
}
