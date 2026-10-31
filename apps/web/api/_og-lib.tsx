import { readFile } from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import satori from 'satori'
import { Resvg } from '@resvg/resvg-js'
import React from 'react'
import type { ReactNode } from 'react'

export const API_URL =
  process.env.API_URL ??
  process.env.RAILWAY_API_URL ??
  'https://api-production-6ec67.up.railway.app'

export const SITE_URL = 'https://hackproof-six.vercel.app'

export interface OgProject {
  project_id: string
  full_name: string | null
  description: string | null
  tier: 'verified' | 'likely' | 'possible' | 'unattributed'
  track: 'genesis' | 'scale' | null
  contracts: number
  stars: number | null
  forks: number | null
  language: string | null
  owner: string | null
  owner_avatar: string | null
  award: string | null
}

export interface OgTimelinePoint {
  hour: string
  contracts: number
}

const tierLabel: Record<OgProject['tier'], string> = {
  verified: 'Verified on-chain',
  likely: 'Code only',
  possible: 'Possible',
  unattributed: 'No repo',
}

const trackLabel: Record<NonNullable<OgProject['track']>, string> = {
  genesis: 'Genesis',
  scale: 'Scale',
}

const FONT_DIR = path.join(path.dirname(fileURLToPath(import.meta.url)), '_fonts')

let fontCache: Record<string, ArrayBuffer> | null = null

async function fonts() {
  if (fontCache) return fontCache
  const [regular, semibold] = await Promise.all([
    readFile(path.join(FONT_DIR, 'Outfit-400.ttf')),
    readFile(path.join(FONT_DIR, 'Outfit-600.ttf')),
  ])
  fontCache = {
    regular: regular.buffer.slice(regular.byteOffset, regular.byteOffset + regular.byteLength),
    semibold: semibold.buffer.slice(semibold.byteOffset, semibold.byteOffset + semibold.byteLength),
  }
  return fontCache
}

export async function fetchProject(projectId: string): Promise<OgProject | null> {
  const url = `${API_URL}/api/projects/${projectId}`
  const response = await fetch(url, {
    headers: { Accept: 'application/json' },
  })
  if (!response.ok) return null
  const data = (await response.json()) as { project: OgProject }
  return data.project ?? null
}

export async function fetchTimeline(): Promise<OgTimelinePoint[]> {
  const response = await fetch(`${API_URL}/api/timeline`, {
    headers: { Accept: 'application/json' },
  })
  if (!response.ok) return []
  const data = (await response.json()) as OgTimelinePoint[]
  return Array.isArray(data) ? data : []
}

function projectName(project: OgProject) {
  return project.full_name || project.project_id.replace(/^repo:/, '') || 'Project'
}

function shortDescription(project: OgProject, limit = 160) {
  const text = project.description?.trim() ?? 'HackMeridian 2026 submission on Stellar'
  return text.length > limit ? `${text.slice(0, limit - 1)}…` : text
}

function row(label: string, value: ReactNode, key: string) {
  return (
    <div
      key={key}
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: 2,
        borderLeft: '2px solid rgba(0,0,0,0.14)',
        paddingLeft: 14,
      }}
    >
      <div style={{ display: 'flex', fontSize: 24, fontWeight: 500, color: 'rgba(15,15,15,0.55)' }}>
        {label}
      </div>
      <div style={{ display: 'flex', fontSize: 38, fontWeight: 600, color: '#0f0f0f' }}>
        {value}
      </div>
    </div>
  )
}

async function svgCard(children: ReactNode) {
  const { regular, semibold } = await fonts()
  return satori(
    <div
      style={{
        width: 1200,
        height: 630,
        display: 'flex',
        flexDirection: 'column',
        backgroundColor: '#f6f7f8',
        color: '#0f0f0f',
        fontFamily: 'Outfit',
        padding: '56px 64px',
        boxSizing: 'border-box',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            width: 44,
            height: 44,
            borderRadius: 10,
            backgroundColor: '#fdda24',
            color: '#0f0f0f',
            fontSize: 26,
            fontWeight: 600,
          }}
        >
          HP
        </div>
        <div style={{ display: 'flex', fontSize: 26, fontWeight: 600, letterSpacing: '0.02em' }}>
          HackProof
        </div>
        <div
          style={{
            display: 'flex',
            marginLeft: 'auto',
            alignItems: 'center',
            gap: 8,
            fontSize: 22,
            color: 'rgba(15,15,15,0.6)',
          }}
        >
          <span
            style={{
              display: 'flex',
              width: 10,
              height: 10,
              borderRadius: 999,
              backgroundColor: '#00a7b5',
            }}
          />
          HackMeridian 2026
        </div>
      </div>
      <div style={{ display: 'flex', flex: 1, flexDirection: 'column', justifyContent: 'center' }}>
        {children}
      </div>
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          borderTop: '2px solid rgba(15,15,15,0.1)',
          paddingTop: 24,
          fontSize: 22,
          color: 'rgba(15,15,15,0.55)',
        }}
      >
        <div style={{ display: 'flex' }}>
          browse.hackproof · submissions rebuilt from Stellar testnet
        </div>
        <div style={{ display: 'flex' }}>hackproof-six.vercel.app</div>
      </div>
    </div>,
    {
      width: 1200,
      height: 630,
      fonts: [
        { name: 'Outfit', data: regular, weight: 400, style: 'normal' },
        { name: 'Outfit', data: semibold, weight: 600, style: 'normal' },
      ],
    },
  )
}

export async function renderProjectCard(project: OgProject): Promise<Buffer> {
  const svg = await svgCard(
    <>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 10, marginBottom: 28 }}>
        <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
          {project.award && (
            <span
              style={{
                display: 'flex',
                borderRadius: 999,
                padding: '6px 14px',
                fontSize: 20,
                fontWeight: 600,
                backgroundColor: '#fdda24',
                color: '#0f0f0f',
              }}
            >
              {project.award}
            </span>
          )}
          <span
            style={{
              display: 'flex',
              borderRadius: 999,
              padding: '6px 14px',
              fontSize: 20,
              fontWeight: 600,
              border: '2px solid rgba(15,15,15,0.35)',
              color: '#0f0f0f',
            }}
          >
            {tierLabel[project.tier]}
          </span>
          {project.track && (
            <span
              style={{
                display: 'flex',
                borderRadius: 999,
                padding: '6px 14px',
                fontSize: 20,
                color: 'rgba(15,15,15,0.65)',
                border: '2px solid rgba(15,15,15,0.14)',
              }}
            >
              {trackLabel[project.track]}
            </span>
          )}
        </div>
      </div>
      <div
        style={{ display: 'flex', fontSize: 72, fontWeight: 600, lineHeight: 1.08, maxWidth: 900 }}
      >
        {projectName(project)}
      </div>
      <div
        style={{
          display: 'flex',
          marginTop: 18,
          fontSize: 30,
          lineHeight: 1.35,
          color: 'rgba(15,15,15,0.68)',
          maxWidth: 860,
        }}
      >
        {shortDescription(project)}
      </div>
      <div style={{ display: 'flex', gap: 48, marginTop: 40 }}>
        {row('Contracts deployed', project.contracts.toLocaleString('en'), 'contracts')}
        {project.stars !== null && row('Stars', project.stars.toLocaleString('en'), 'stars')}
        {project.forks !== null && row('Forks', project.forks.toLocaleString('en'), 'forks')}
        {project.language && row('Language', project.language, 'language')}
      </div>
    </>,
  )
  const resvg = new Resvg(svg, {
    fitTo: { mode: 'width', value: 1200 },
  })
  const png = resvg.render()
  return png.asPng()
}

export async function renderDefaultCard(timeline: OgTimelinePoint[]): Promise<Buffer> {
  const bars = timeline.length
    ? timeline
    : Array.from({ length: 24 }, (_, i) => ({
        hour: `2026-10-25T${String(i).padStart(2, '0')}:00:00Z`,
        contracts: 0,
      }))
  const max = Math.max(1, ...bars.map((b) => b.contracts))

  const svg = await svgCard(
    <>
      <div style={{ display: 'flex', fontSize: 66, fontWeight: 600, lineHeight: 1.08 }}>
        HackMeridian 2026
      </div>
      <div style={{ display: 'flex', marginTop: 14, fontSize: 28, color: 'rgba(15,15,15,0.68)' }}>
        OSS submissions, rebuilt from Stellar testnet and linked to their GitHub repos.
      </div>
      <div style={{ display: 'flex', alignItems: 'flex-end', gap: 3, marginTop: 36, height: 170 }}>
        {bars.map((b) => (
          <div
            key={b.hour}
            style={{
              display: 'flex',
              flex: 1,
              height: `${Math.max(4, Math.round((b.contracts / max) * 100))}%`,
              backgroundColor: b.contracts > 0 ? '#00a7b5' : 'rgba(15,15,15,0.08)',
              borderRadius: 2,
            }}
          />
        ))}
      </div>
      <div style={{ display: 'flex', marginTop: 18, fontSize: 24, color: 'rgba(15,15,15,0.5)' }}>
        {timeline.length
          ? `contracts deployed per hour · peak ${max.toLocaleString('en')}`
          : 'contracts deployed per hour'}
      </div>
    </>,
  )
  const resvg = new Resvg(svg, {
    fitTo: { mode: 'width', value: 1200 },
  })
  const png = resvg.render()
  return png.asPng()
}

export function escapeHtml(value: string) {
  return value
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;')
}

export function projectMeta(project: OgProject) {
  const title = `${projectName(project)} — HackMeridian 2026`
  const description = `${tierLabel[project.tier]} · ${project.contracts.toLocaleString('en')} contracts deployed${project.track ? ` · ${trackLabel[project.track]}` : ''}${project.description ? ` — ${shortDescription(project, 140)}` : ''}`
  return { title, description }
}

export { tierLabel, trackLabel }
