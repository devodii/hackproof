import { ImageResponse } from '@vercel/og'

import type { Card } from './_card.ts'
import { layout } from './_layout.ts'

export const SIZE = { width: 1200, height: 630 }

async function font(name: string) {
  const url = new URL(`./_fonts/${name}.woff`, import.meta.url)
  return (await fetch(url)).arrayBuffer()
}

async function image(url: string | null) {
  if (!url) return null
  try {
    const response = await fetch(url)
    if (!response.ok) return null
    const type = response.headers.get('content-type') ?? 'image/png'
    const bytes = new Uint8Array(await response.arrayBuffer())
    let binary = ''
    bytes.forEach((byte) => (binary += String.fromCharCode(byte)))
    return `data:${type};base64,${btoa(binary)}`
  } catch {
    return null
  }
}

export async function render(card: Card) {
  const [regular, italic, sans, semibold, avatar] = await Promise.all([
    font('InstrumentSerif-Regular'),
    font('InstrumentSerif-Italic'),
    font('Outfit-Regular'),
    font('Outfit-SemiBold'),
    image(card.avatar),
  ])
  return new ImageResponse(layout(card, avatar) as never, {
    ...SIZE,
    headers: { 'cache-control': 'public, max-age=0, s-maxage=3600, stale-while-revalidate=86400' },
    fonts: [
      { name: 'Instrument Serif', data: regular, weight: 400, style: 'normal' },
      { name: 'Instrument Serif', data: italic, weight: 400, style: 'italic' },
      { name: 'Outfit', data: sans, weight: 400, style: 'normal' },
      { name: 'Outfit', data: semibold, weight: 600, style: 'normal' },
    ],
  })
}
