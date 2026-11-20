import { describe } from './_card'
import { render } from './_render'

export const config = { runtime: 'edge' }

export default async function handler(request: Request) {
  const url = new URL(request.url)
  const api = process.env.VITE_API_URL ?? process.env.API_URL ?? ''
  const card = await describe(api.replace(/\/$/, ''), url.searchParams.get('path') ?? '/')
  return render(card)
}
