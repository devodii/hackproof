import { cp, mkdir, readdir, readFile, writeFile } from 'node:fs/promises'
import path from 'node:path'
import { parse, stringify } from 'yaml'

const root = path.resolve(import.meta.dirname, '../../..')
const source = path.join(root, 'data')
const target = path.resolve(import.meta.dirname, '../dist/data')
const LEGACY = { event: 'hackmeridian-2026', year: '2026' }

const entries = await readdir(source, { withFileTypes: true })
const published = entries.filter(
  (entry) =>
    (entry.isDirectory() && /^\d{4}$/.test(entry.name)) || entry.name.startsWith('schema-'),
)
if (!published.some((entry) => entry.name === LEGACY.year)) {
  throw new Error(`data/${LEGACY.year} is missing, nothing to publish`)
}

await mkdir(target, { recursive: true })
for (const entry of published) {
  await cp(path.join(source, entry.name), path.join(target, entry.name), { recursive: true })
}

const folder = path.join(source, LEGACY.year)
const files = (await readdir(folder)).filter((name) => name.endsWith('.yml')).sort()
const projects = await Promise.all(
  files.map(async (name) => parse(await readFile(path.join(folder, name), 'utf8'))),
)
const combined = { event: LEGACY.event, projects }

const legacy = path.join(target, LEGACY.event)
await mkdir(legacy, { recursive: true })
await writeFile(path.join(legacy, 'projects.json'), `${JSON.stringify(combined, null, 2)}\n`)
await writeFile(path.join(legacy, 'projects.yml'), stringify(combined, { lineWidth: 120 }))
console.log(`published ${files.length} projects from data/${LEGACY.year} to dist/data`)
