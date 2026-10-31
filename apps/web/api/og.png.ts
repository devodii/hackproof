import type { VercelRequest, VercelResponse } from '@vercel/node'
import { fetchProject, fetchTimeline, renderDefaultCard, renderProjectCard } from './_og-lib'

export default async function handler(req: VercelRequest, res: VercelResponse) {
  const projectId = typeof req.query.project === 'string' ? req.query.project : ''

  try {
    let png: Buffer
    if (projectId) {
      const project = await fetchProject(projectId)
      if (!project) {
        res.status(404).setHeader('Cache-Control', 'public, s-maxage=300')
        return res.end('project not found')
      }
      png = await renderProjectCard(project)
    } else {
      const timeline = await fetchTimeline()
      png = await renderDefaultCard(timeline)
    }

    res.status(200)
    res.setHeader('Content-Type', 'image/png')
    res.setHeader('Cache-Control', 'public, s-maxage=3600, max-age=600')
    res.setHeader('Content-Length', String(png.length))
    return res.end(png)
  } catch (error) {
    console.error('og.png handler error:', error)
    res.status(500).setHeader('Cache-Control', 'no-store')
    return res.end('error rendering og image')
  }
}
