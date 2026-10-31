import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const root = path.resolve(__dirname, '..')

const enPath = path.join(root, 'src', 'i18n', 'locales', 'en.json')
const ptPath = path.join(root, 'src', 'i18n', 'locales', 'pt.json')

if (!fs.existsSync(enPath) || !fs.existsSync(ptPath)) {
  console.error('Error: Translation files missing!')
  process.exit(1)
}

const en = JSON.parse(fs.readFileSync(enPath, 'utf8'))
const pt = JSON.parse(fs.readFileSync(ptPath, 'utf8'))

function flattenKeys(obj, prefix = '') {
  let keys = {}
  for (const [k, v] of Object.entries(obj)) {
    const fullKey = prefix ? `${prefix}.${k}` : k
    if (typeof v === 'object' && v !== null && !Array.isArray(v)) {
      Object.assign(keys, flattenKeys(v, fullKey))
    } else {
      keys[fullKey] = v
    }
  }
  return keys
}

const enKeys = flattenKeys(en)
const ptKeys = flattenKeys(pt)

let errors = 0

// 1. Verify key parity
for (const key of Object.keys(enKeys)) {
  if (!(key in ptKeys)) {
    console.error(`Missing translation in pt.json: ${key}`)
    errors++
  } else if (!ptKeys[key] || typeof ptKeys[key] !== 'string' || ptKeys[key].trim() === '') {
    console.error(`Empty translation in pt.json: ${key}`)
    errors++
  }
}

for (const key of Object.keys(ptKeys)) {
  if (!(key in enKeys)) {
    console.error(`Extraneous key in pt.json not in en.json: ${key}`)
    errors++
  }
}

console.log(`Verified ${Object.keys(enKeys).length} translation keys parity between EN and PT.`)

// 2. Scan critical components for leftover hardcoded strings
const filesToCheck = [
  'src/components/layout/site-header.tsx',
  'src/components/layout/site-footer.tsx',
  'src/pages/home.tsx',
  'src/pages/builder.tsx',
  'src/components/overview.tsx',
]

const forbiddenSubstrings = [
  '> Winners',
  '>Open Source',
  'Independent project, not affiliated',
  'HackMeridian 2026, rebuilt from the chain.',
  'Contracts deployed, per hour over the 27 hour window',
]

for (const rel of filesToCheck) {
  const filePath = path.join(root, rel)
  if (fs.existsSync(filePath)) {
    const content = fs.readFileSync(filePath, 'utf8')
    for (const forbidden of forbiddenSubstrings) {
      if (content.includes(forbidden)) {
        console.error(`Found hardcoded string "${forbidden}" in ${rel}`)
        errors++
      }
    }
  }
}

if (errors > 0) {
  console.error(`\nCI i18n Check FAILED with ${errors} error(s).`)
  process.exit(1)
} else {
  console.log('CI i18n Check PASSED: No hardcoded strings found and all keys match!')
  process.exit(0)
}
