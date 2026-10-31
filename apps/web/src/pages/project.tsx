import { ExternalLinkIcon } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { useParams } from 'react-router'

import { AwardBadge } from '@/components/award-badge'
import { Contributors } from '@/components/contributors'
import { DataTable } from '@/components/data-table'
import { ActivitySections } from '@/components/explorer/activity-sections'
import { integrationColumns, linkColumns } from '@/components/explorer/columns'
import { ProjectSkeleton } from '@/components/page-skeletons'
import { DetailError } from '@/components/query-state'
import { Section } from '@/components/section'
import { TierBadge } from '@/components/tier-badge'
import { TrackBadge } from '@/components/track-badge'
import { Accordion } from '@/components/ui/accordion'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Badge } from '@/components/ui/badge'
import { useHackWindow } from '@/hooks/use-hack-window'
import { useProject } from '@/hooks/use-project'
import { flagEmoji, footprintLabel, isWithin, projectName } from '@/lib/format'
import { githubUrl } from '@/lib/links'

export function ProjectPage() {
  const projectId = useParams()['*'] ?? ''
  const { data, isPending, error } = useProject(projectId)
  const { data: hackWindow } = useHackWindow()
  const { t, i18n } = useTranslation()

  if (isPending) return <ProjectSkeleton />
  if (error) return <DetailError error={error} subject="project" />

  const { project, links, integration_uses, contributors, contracts, wasm_uploads, failed_txs } =
    data
  const name = projectName(project.project_id)
  const direct = links.filter((link) => link.method !== 'footprint')
  const derived = links.length - direct.length
  const packages = Object.entries(project.dependencies?.packages ?? {})
  const reasons = [
    isWithin(project.created_at, hackWindow) && t('project.createdDuringHack'),
    project.stellar_added_in_window && t('project.addedStellarDuringHack'),
  ].filter(Boolean) as string[]
  const locale = i18n.language.startsWith('pt') ? 'pt' : 'en'
  const inclusion = reasons.length
    ? new Intl.ListFormat(locale, { type: 'conjunction' }).format(reasons)
    : t('project.defaultInclusion')

  return (
    <div className="flex flex-col gap-8">
      <header className="flex flex-col gap-3">
        <div className="flex flex-wrap items-center gap-x-3 gap-y-2">
          <Avatar className="shrink-0">
            {project.owner_avatar && (
              <AvatarImage src={project.owner_avatar} alt={project.owner ?? ''} />
            )}
            <AvatarFallback>{name.slice(0, 2).toUpperCase()}</AvatarFallback>
          </Avatar>
          <h1 className="min-w-0 text-3xl leading-none wrap-break-word sm:text-5xl">{name}</h1>
          {project.country && <span title={project.country}>{flagEmoji(project.country)}</span>}
          <TierBadge tier={project.tier} />
          <AwardBadge place={project.award} />
          <TrackBadge track={project.track} />
          <Badge variant="outline">{t(`footprint.${project.footprint}`, { defaultValue: footprintLabel[project.footprint] })}</Badge>
        </div>

        {project.description && (
          <p className="max-w-3xl text-lg text-muted-foreground">{project.description}</p>
        )}

        <div className="flex flex-wrap items-center gap-x-4 gap-y-2 text-sm text-muted-foreground">
          {project.url && (
            <a
              href={project.url}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-1 hover:text-foreground"
            >
              {project.full_name ?? name}
              <ExternalLinkIcon className="size-3.5" />
            </a>
          )}
          {project.homepage && (
            <a
              href={project.homepage}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-1 hover:text-foreground"
            >
              {project.homepage}
              <ExternalLinkIcon className="size-3.5" />
            </a>
          )}
          {project.full_name &&
            project.window_commits !== null &&
            project.total_commits !== null &&
            hackWindow && (
              <a
                href={githubUrl.commits(project.full_name, hackWindow)}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-1 hover:text-foreground"
              >
                {t('project.commitsInWindow', { window: project.window_commits, total: project.total_commits })}
                <ExternalLinkIcon className="size-3.5" />
              </a>
            )}
        </div>
        {project.tier !== 'verified' && (
          <p className="text-sm text-muted-foreground">{t('project.includedBecause', { inclusion })}</p>
        )}
        {packages.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {packages.map(([pkg, version]) => (
              <Badge key={pkg} variant="outline" className="font-mono">
                {pkg}
                {version && ` ${version}`}
              </Badge>
            ))}
          </div>
        )}
      </header>
      <Accordion multiple defaultValue={['evidence', 'integrations']}>
        {integration_uses.length > 0 && (
          <Section value="integrations" title={t('project.sections.integrations')} count={integration_uses.length}>
            <DataTable
              columns={integrationColumns(project.full_name ?? '')}
              rows={integration_uses}
              rowKey={(row) => `${row.slug}:${row.method}:${row.evidence}`}
            />
          </Section>
        )}
        {contributors.length > 0 && (
          <Section value="contributors" title={t('project.sections.contributors')} count={contributors.length}>
            <Contributors contributors={contributors} />
          </Section>
        )}
        {direct.length > 0 && (
          <Section value="evidence" title={t('project.sections.evidence')} count={direct.length}>
            <DataTable
              columns={linkColumns(project.full_name ?? '')}
              rows={direct}
              rowKey={(row) => `${row.subject_kind}:${row.subject}`}
            />
            {derived > 0 && (
              <p className="mt-3 text-sm text-muted-foreground">
                {t('project.derivedNotice', { count: derived })}
              </p>
            )}
          </Section>
        )}
        <ActivitySections contracts={contracts} wasmUploads={wasm_uploads} failedTxs={failed_txs} />
      </Accordion>
    </div>
  )
}
