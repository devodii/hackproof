import { readFileSync } from 'node:fs'

import { Resvg } from '@resvg/resvg-js'
import satori from 'satori'

import type { Card } from './_card'
import { layout } from './_layout'

export const SIZE = { width: 1200, height: 630 }

const font = (name: string) => readFileSync(new URL(`./_fonts/${name}.woff`, import.meta.url))

async function image(url: string | null) {
  if (!url) return null
  try {
    const response = await fetch(url)
    if (!response.ok) return null
    const type = response.headers.get('content-type') ?? 'image/png'
    return `data:${type};base64,${Buffer.from(await response.arrayBuffer()).toString('base64')}`
  } catch {
    return null
  }
}

export async function render(card: Card) {
  const svg = await satori(layout(card, await image(card.avatar)) as never, {
    ...SIZE,
    fonts: [
      {
        name: 'Instrument Serif',
        data: font('InstrumentSerif-Regular'),
        weight: 400,
        style: 'normal',
      },
      {
        name: 'Instrument Serif',
        data: font('InstrumentSerif-Italic'),
        weight: 400,
        style: 'italic',
      },
      { name: 'Outfit', data: font('Outfit-Regular'), weight: 400, style: 'normal' },
      { name: 'Outfit', data: font('Outfit-SemiBold'), weight: 600, style: 'normal' },
    ],
  })
  const png = new Resvg(svg, { fitTo: { mode: 'width', value: SIZE.width } }).render().asPng()
  return new Response(new Uint8Array(png), {
    headers: {
      'content-type': 'image/png',
      'cache-control': 'public, max-age=0, s-maxage=3600, stale-while-revalidate=86400',
    },
  })
}
