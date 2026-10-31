import type { VercelRequest, VercelResponse } from '@vercel/node'
import { escapeHtml, fetchProject, projectMeta, SITE_URL } from './_og-lib'

export default async function handler(req: VercelRequest, res: VercelResponse) {
  const projectId = typeof req.query.project === 'string' ? req.query.project : ''
  const origin =
    req.headers['x-forwarded-proto'] === 'https'
      ? `https://${req.headers['x-forwarded-host'] ?? SITE_URL.replace(/^https:\/\//, '')}`
      : SITE_URL

  try {
    const project = projectId ? await fetchProject(projectId) : null

    if (projectId && !project) {
      res.status(404).setHeader('Cache-Control', 'public, s-maxage=300')
      return res.send(
        `<!doctype html><html><head><meta charset="utf-8"><title>Not found — HackMeridian 2026</title>
<meta property="og:title" content="Project not found — HackMeridian 2026">
<meta property="og:description" content="The project you are looking for is not in the HackMeridian 2026 dataset.">
<meta name="robots" content="noindex"></head><body><h1>Project not found</h1></body></html>`,
      )
    }

    const { title, description } = project
      ? projectMeta(project)
      : {
          title: 'HackMeridian 2026',
          description:
            'OSS submissions, rebuilt from Stellar testnet and linked to their GitHub repos.',
        }
    const image = `${origin}/api/og.png${projectId ? `?project=${encodeURIComponent(projectId)}` : ''}`

    res.status(200).setHeader('Content-Type', 'text/html; charset=utf-8')
    res.setHeader('Cache-Control', 'public, s-maxage=600')
    return res.send(`<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>${escapeHtml(title)}</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="${escapeHtml(description)}">
<meta property="og:title" content="${escapeHtml(title)}">
<meta property="og:description" content="${escapeHtml(description)}">
<meta property="og:type" content="website">
<meta property="og:url" content="${origin}${projectId ? `/project/${projectId}` : '/'}">
<meta property="og:image" content="${image}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:type" content="image/png">
<meta property="og:site_name" content="HackProof">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="${escapeHtml(title)}">
<meta name="twitter:description" content="${escapeHtml(description)}">
<meta name="twitter:image" content="${image}">
</head>
<body>
<h1>${escapeHtml(title)}</h1>
<p>${escapeHtml(description)}</p>
<p><a href="${origin}${projectId ? `/project/${projectId}` : '/'}">Open in the HackMeridian 2026 explorer</a></p>
</body>
</html>`)
  } catch (error) {
    console.error('og handler error:', error)
    res.status(500).setHeader('Cache-Control', 'no-store')
    return res.send(
      '<!doctype html><html><head><meta charset="utf-8"><title>Error</title><meta name="robots" content="noindex"></head><body><h1>Error rendering preview</h1></body></html>',
    )
  }
}
