import { describe, descriptionOf } from './_card.ts'

export const config = { runtime: 'edge' }

const escape = (value: string) =>
  value.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;')

export default async function handler(request: Request) {
  const url = new URL(request.url)
  const path = url.searchParams.get('path') ?? '/'
  const api = (process.env.VITE_API_URL ?? process.env.API_URL ?? '').replace(/\/$/, '')
  const card = await describe(api, path)
  const origin = url.origin
  const page = `${origin}${path}`
  const image = `${origin}/api/og?path=${encodeURIComponent(path)}`
  const title = escape(card.title_for_page)
  const description = escape(descriptionOf(card))

  const html = `<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>${title}</title>
    <meta name="description" content="${description}" />
    <link rel="canonical" href="${escape(page)}" />
    <meta property="og:type" content="website" />
    <meta property="og:site_name" content="HackProof" />
    <meta property="og:title" content="${title}" />
    <meta property="og:description" content="${description}" />
    <meta property="og:url" content="${escape(page)}" />
    <meta property="og:image" content="${escape(image)}" />
    <meta property="og:image:width" content="1200" />
    <meta property="og:image:height" content="630" />
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="${title}" />
    <meta name="twitter:description" content="${description}" />
    <meta name="twitter:image" content="${escape(image)}" />
  </head>
  <body>${title}</body>
</html>`
  return new Response(html, {
    headers: {
      'content-type': 'text/html; charset=utf-8',
      'cache-control': 'public, max-age=0, s-maxage=3600, stale-while-revalidate=86400',
    },
  })
}
