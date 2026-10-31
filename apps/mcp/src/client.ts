import type {
  Contract,
  CountryCount,
  FailedTx,
  Integration,
  Page,
  Project,
  ProjectDetail,
  Stats,
  TimelinePoint,
  WasmUpload,
} from './types.js'

interface CacheEntry<T> {
  data: T
  etag?: string
  expiresAt: number
  generatedAt: string
}

export interface ApiResponseWithFreshness<T> {
  data: T
  generated_at: string
}

export class HackProofClient {
  private apiBase: string
  private cache: Map<string, CacheEntry<any>> = new Map()
  private defaultTtlMs: number = 60_000 // 60s in-memory cache

  constructor(apiBase?: string) {
    this.apiBase = (
      apiBase ||
      process.env.HACKPROOF_API_URL ||
      'https://hackproof.vercel.app/api'
    ).replace(/\/$/, '')
  }

  private async fetchWithCache<T>(path: string): Promise<ApiResponseWithFreshness<T>> {
    const url = `${this.apiBase}${path.startsWith('/') ? path : `/${path}`}`
    const now = Date.now()
    const cached = this.cache.get(url)

    const headers: Record<string, string> = {
      Accept: 'application/json',
      'User-Agent': 'HackProof-MCP-Server/0.1.0',
    }

    if (cached) {
      if (now < cached.expiresAt) {
        return { data: cached.data, generated_at: cached.generatedAt }
      }
      if (cached.etag) {
        headers['If-None-Match'] = cached.etag
      }
    }

    try {
      const resp = await fetch(url, { headers })

      if (resp.status === 304 && cached) {
        cached.expiresAt = now + this.defaultTtlMs
        return { data: cached.data, generated_at: cached.generatedAt }
      }

      if (!resp.ok) {
        throw new Error(`API error from ${url}: ${resp.status} ${resp.statusText}`)
      }

      const etag = resp.headers.get('ETag') || undefined
      const dateHeader = resp.headers.get('Date')
      const generatedAt = dateHeader
        ? new Date(dateHeader).toISOString()
        : new Date(now).toISOString()

      const data = (await resp.json()) as T

      this.cache.set(url, {
        data,
        etag,
        expiresAt: now + this.defaultTtlMs,
        generatedAt,
      })

      return { data, generated_at: generatedAt }
    } catch (err) {
      // If network fails but we have stale cache, serve stale
      if (cached) {
        return { data: cached.data, generated_at: cached.generatedAt }
      }
      throw err
    }
  }

  async getStats(): Promise<ApiResponseWithFreshness<Stats>> {
    const res = await this.fetchWithCache<Stats>('/stats')
    const stats = res.data
    const generatedAt = stats.generated_at || res.generated_at
    return { data: { ...stats, generated_at: generatedAt }, generated_at: generatedAt }
  }

  async getTimeline(): Promise<ApiResponseWithFreshness<TimelinePoint[]>> {
    return this.fetchWithCache<TimelinePoint[]>('/timeline')
  }

  async getCountries(): Promise<ApiResponseWithFreshness<CountryCount[]>> {
    return this.fetchWithCache<CountryCount[]>('/countries')
  }

  async getIntegrations(): Promise<ApiResponseWithFreshness<Integration[]>> {
    return this.fetchWithCache<Integration[]>('/integrations')
  }

  async getProjects(params?: {
    q?: string
    tier?: string
    track?: string
    integration?: string
    limit?: number
    offset?: number
  }): Promise<ApiResponseWithFreshness<Page<Project>>> {
    const query = new URLSearchParams()
    if (params?.q) query.set('q', params.q)
    if (params?.tier) query.set('tier', params.tier)
    if (params?.track) query.set('track', params.track)
    if (params?.integration) query.set('integration', params.integration)
    if (params?.limit) query.set('limit', params.limit.toString())
    if (params?.offset) query.set('offset', params.offset.toString())

    const qs = query.toString()
    const path = `/projects${qs ? `?${qs}` : ''}`
    return this.fetchWithCache<Page<Project>>(path)
  }

  async getProject(projectId: string): Promise<ApiResponseWithFreshness<ProjectDetail>> {
    return this.fetchWithCache<ProjectDetail>(`/projects/${encodeURIComponent(projectId)}`)
  }

  async getContracts(params?: {
    q?: string
    limit?: number
    offset?: number
  }): Promise<ApiResponseWithFreshness<Page<Contract>>> {
    const query = new URLSearchParams()
    if (params?.q) query.set('q', params.q)
    if (params?.limit) query.set('limit', params.limit.toString())
    if (params?.offset) query.set('offset', params.offset.toString())

    const qs = query.toString()
    return this.fetchWithCache<Page<Contract>>(`/contracts${qs ? `?${qs}` : ''}`)
  }

  async getWasm(params?: {
    q?: string
    limit?: number
    offset?: number
  }): Promise<ApiResponseWithFreshness<Page<WasmUpload>>> {
    const query = new URLSearchParams()
    if (params?.q) query.set('q', params.q)
    if (params?.limit) query.set('limit', params.limit.toString())
    if (params?.offset) query.set('offset', params.offset.toString())

    const qs = query.toString()
    return this.fetchWithCache<Page<WasmUpload>>(`/wasm${qs ? `?${qs}` : ''}`)
  }

  async getFailed(params?: {
    q?: string
    limit?: number
    offset?: number
  }): Promise<ApiResponseWithFreshness<Page<FailedTx>>> {
    const query = new URLSearchParams()
    if (params?.q) query.set('q', params.q)
    if (params?.limit) query.set('limit', params.limit.toString())
    if (params?.offset) query.set('offset', params.offset.toString())

    const qs = query.toString()
    return this.fetchWithCache<Page<FailedTx>>(`/failed${qs ? `?${qs}` : ''}`)
  }
}
