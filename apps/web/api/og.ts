import { describe } from './_card'
import { render } from './_render'

export async function GET(request: Request) {
  const url = new URL(request.url)
  const api = (process.env.VITE_API_URL ?? process.env.API_URL ?? '').replace(/\/$/, '')
  return render(await describe(api, url.searchParams.get('path') ?? '/'))
}
