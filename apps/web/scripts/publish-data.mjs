import { existsSync } from 'node:fs'
import { cp, mkdir, readdir, readFile, writeFile } from 'node:fs/promises'
import path from 'node:path'
import { parse, stringify } from 'yaml'

const root = path.resolve(import.meta.dirname, '../../..')
const source = path.join(root, 'data')
const target = path.resolve(import.meta.dirname, '../dist/data')

const entries = await readdir(source, { withFileTypes: true })
const hackathons = entries.filter((entry) => entry.isDirectory()).map((entry) => entry.name)
if (hackathons.length === 0) throw new Error('data has no hackathon folders, nothing to publish')

for (const hackathon of hackathons) {
  const folder = path.join(source, hackathon, 'projects')
  if (!existsSync(folder)) continue
  const files = (await readdir(folder)).filter((name) => name.endsWith('.yml')).sort()
  const projects = await Promise.all(
    files.map(async (name) => parse(await readFile(path.join(folder, name), 'utf8'))),
  )
  const combined = { hackathon, projects }
  const out = path.join(target, hackathon)

  await mkdir(out, { recursive: true })
  await cp(folder, path.join(out, 'projects'), { recursive: true })
  await writeFile(path.join(out, 'projects.json'), `${JSON.stringify(combined, null, 2)}\n`)
  await writeFile(path.join(out, 'projects.yml'), stringify(combined, { lineWidth: 120 }))
  console.log(`published ${files.length} projects of ${hackathon} to dist/data/${hackathon}`)
}
