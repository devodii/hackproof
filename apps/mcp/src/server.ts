import { Server } from '@modelcontextprotocol/sdk/server/index.js'
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  type Tool,
} from '@modelcontextprotocol/sdk/types.js'

import { HackProofClient } from './client.js'

const TOOLS: Tool[] = [
  {
    name: 'list_hackathons',
    description: 'List all hackathons indexed and verified by HackProof, including HackMeridian 2026.',
    inputSchema: {
      type: 'object',
      properties: {},
      additionalProperties: false,
    },
  },
  {
    name: 'get_summary',
    description: 'Get high-level summary metrics for HackMeridian (projects, verified projects, total contracts, builders, contributors, countries, wasm uploads, and freshness timestamp).',
    inputSchema: {
      type: 'object',
      properties: {},
      additionalProperties: false,
    },
  },
  {
    name: 'query_projects',
    description: 'Search and filter HackProof projects by keyword, evidence tier (verified, likely, possible), track (genesis, scale), or integration partner.',
    inputSchema: {
      type: 'object',
      properties: {
        q: { type: 'string', description: 'Search term across project name, description or repository' },
        tier: { type: 'string', enum: ['verified', 'likely', 'possible', 'unattributed'], description: 'Filter by evidence tier' },
        track: { type: 'string', enum: ['genesis', 'scale'], description: 'Filter by track' },
        integration: { type: 'string', description: 'Filter by integration partner slug (e.g. privy, trustless-work)' },
        limit: { type: 'number', description: 'Number of results to return (default 20, max 100)' },
        offset: { type: 'number', description: 'Offset for pagination' },
      },
      additionalProperties: false,
    },
  },
  {
    name: 'get_project',
    description: 'Get in-depth breakdown for a specific HackProof project by project ID or repo full name, including evidence matches, contributors, contracts deployed, wasm uploads, and failed transactions.',
    inputSchema: {
      type: 'object',
      properties: {
        project_id: { type: 'string', description: 'Project ID (e.g. "repo:org/name") or repository full name' },
      },
      required: ['project_id'],
      additionalProperties: false,
    },
  },
  {
    name: 'get_contract',
    description: 'Lookup a deployed Soroban contract on Stellar testnet by contract ID or search query to view its deployer, wasm hash, transaction hash, and timestamp.',
    inputSchema: {
      type: 'object',
      properties: {
        contract_id: { type: 'string', description: 'Stellar contract ID (C...) or search term' },
      },
      required: ['contract_id'],
      additionalProperties: false,
    },
  },
  {
    name: 'hourly',
    description: 'Get the hourly timeline of Soroban contract deployments across the entire 27-hour hackathon window.',
    inputSchema: {
      type: 'object',
      properties: {},
      additionalProperties: false,
    },
  },
  {
    name: 'distributions',
    description: 'Get comprehensive distribution metrics: builder geographic origin by country, evidence tier breakdown, and track distributions.',
    inputSchema: {
      type: 'object',
      properties: {},
      additionalProperties: false,
    },
  },
  {
    name: 'top_errors',
    description: 'Get the most common Soroban and Stellar transaction failure kinds and error codes recorded during the hack window.',
    inputSchema: {
      type: 'object',
      properties: {
        limit: { type: 'number', description: 'Max error transactions to inspect (default 50)' },
      },
      additionalProperties: false,
    },
  },
  {
    name: 'compare_idea',
    description: 'Compare an idea or proposal against all HackProof submissions using keyword matching over project names, descriptions and topics, returning the closest projects with matched terms.',
    inputSchema: {
      type: 'object',
      properties: {
        text: { type: 'string', description: 'The idea, thesis or description to compare against existing projects' },
      },
      required: ['text'],
      additionalProperties: false,
    },
  },
  {
    name: 'methodology',
    description: 'Return the official HackProof methodology explaining evidence tiers (verified vs likely vs possible), repo-to-chain matching, and testnet reconstruction rules.',
    inputSchema: {
      type: 'object',
      properties: {},
      additionalProperties: false,
    },
  },
]

export function createMcpServer(client?: HackProofClient) {
  const apiClient = client || new HackProofClient()

  const server = new Server(
    {
      name: 'hackproof-mcp',
      version: '0.1.0',
    },
    {
      capabilities: {
        tools: {},
      },
    },
  )

  server.setRequestHandler(ListToolsRequestSchema, async () => {
    return { tools: TOOLS }
  })

  server.setRequestHandler(CallToolRequestSchema, async (request) => {
    const { name, arguments: args = {} } = request.params

    try {
      switch (name) {
        case 'list_hackathons': {
          const statsRes = await apiClient.getStats()
          const payload = {
            hackathons: [
              {
                slug: 'hackmeridian-2026',
                name: 'HackMeridian 2026',
                network: 'stellar-testnet',
                window: {
                  start: '2026-10-17T09:00:00Z',
                  end: '2026-10-18T12:00:00Z',
                  duration_hours: 27,
                },
                location: 'Lisbon, Portugal',
                tracks: ['genesis', 'scale'],
                total_projects: statsRes.data.projects,
              },
            ],
            generated_at: statsRes.generated_at,
          }
          return {
            content: [{ type: 'text', text: JSON.stringify(payload, null, 2) }],
          }
        }

        case 'get_summary': {
          const res = await apiClient.getStats()
          return {
            content: [{ type: 'text', text: JSON.stringify(res, null, 2) }],
          }
        }

        case 'query_projects': {
          const limit = Math.min(Number(args.limit) || 20, 100)
          const offset = Number(args.offset) || 0
          const res = await apiClient.getProjects({
            q: typeof args.q === 'string' ? args.q : undefined,
            tier: typeof args.tier === 'string' ? args.tier : undefined,
            track: typeof args.track === 'string' ? args.track : undefined,
            integration: typeof args.integration === 'string' ? args.integration : undefined,
            limit,
            offset,
          })
          const payload = {
            total: res.data.total,
            count: res.data.items.length,
            projects: res.data.items,
            generated_at: res.generated_at,
          }
          return {
            content: [{ type: 'text', text: JSON.stringify(payload, null, 2) }],
          }
        }

        case 'get_project': {
          const projectId = String(args.project_id || '')
          if (!projectId) {
            return {
              isError: true,
              content: [{ type: 'text', text: 'Missing required argument: project_id' }],
            }
          }
          const formattedId = projectId.startsWith('repo:') || projectId.startsWith('acct:')
            ? projectId
            : `repo:${projectId}`
          const res = await apiClient.getProject(formattedId)
          return {
            content: [{ type: 'text', text: JSON.stringify(res, null, 2) }],
          }
        }

        case 'get_contract': {
          const contractId = String(args.contract_id || '')
          const res = await apiClient.getContracts({ q: contractId, limit: 10 })
          const payload = {
            query: contractId,
            matched_contracts: res.data.items,
            generated_at: res.generated_at,
          }
          return {
            content: [{ type: 'text', text: JSON.stringify(payload, null, 2) }],
          }
        }

        case 'hourly': {
          const res = await apiClient.getTimeline()
          const payload = {
            timeline: res.data,
            peak_hour: res.data.reduce(
              (best, point) => (point.contracts > best.contracts ? point : best),
              res.data[0] || { hour: '', contracts: 0 },
            ),
            generated_at: res.generated_at,
          }
          return {
            content: [{ type: 'text', text: JSON.stringify(payload, null, 2) }],
          }
        }

        case 'distributions': {
          const [countriesRes, statsRes] = await Promise.all([
            apiClient.getCountries(),
            apiClient.getStats(),
          ])
          const payload = {
            countries: countriesRes.data,
            tiers: {
              verified: statsRes.data.verified_projects,
              likely: statsRes.data.likely_projects,
              possible: statsRes.data.possible_projects,
              unattributed_accounts: statsRes.data.unattributed_accounts,
            },
            total_projects: statsRes.data.projects,
            generated_at: statsRes.generated_at,
          }
          return {
            content: [{ type: 'text', text: JSON.stringify(payload, null, 2) }],
          }
        }

        case 'top_errors': {
          const limit = Math.min(Number(args.limit) || 50, 200)
          const res = await apiClient.getFailed({ limit })

          const errorFrequency: Record<string, number> = {}
          const kindFrequency: Record<string, number> = {}
          for (const tx of res.data.items) {
            errorFrequency[tx.result_code] = (errorFrequency[tx.result_code] || 0) + 1
            kindFrequency[tx.kind] = (kindFrequency[tx.kind] || 0) + 1
          }

          const sortedErrors = Object.entries(errorFrequency)
            .sort((a, b) => b[1] - a[1])
            .map(([code, count]) => ({ code, count }))

          const payload = {
            total_failed_txs_sampled: res.data.items.length,
            top_result_codes: sortedErrors,
            operations_distribution: kindFrequency,
            sample_recent_failures: res.data.items.slice(0, 10),
            generated_at: res.generated_at,
          }
          return {
            content: [{ type: 'text', text: JSON.stringify(payload, null, 2) }],
          }
        }

        case 'compare_idea': {
          const text = String(args.text || '').toLowerCase()
          if (!text) {
            return {
              isError: true,
              content: [{ type: 'text', text: 'Missing required argument: text' }],
            }
          }

          // Fetch projects
          const res = await apiClient.getProjects({ limit: 100 })
          const stopWords = new Set([
            'a', 'an', 'and', 'the', 'in', 'on', 'of', 'for', 'to', 'with', 'by',
            'is', 'are', 'was', 'were', 'at', 'from', 'as', 'that', 'this', 'it',
          ])
          const tokens = text
            .split(/[\s,.;:!?/()\[\]{}]+/)
            .map((t) => t.trim().toLowerCase())
            .filter((t) => t.length > 2 && !stopWords.has(t))

          const scored = res.data.items.map((project) => {
            const searchable = [
              project.full_name || '',
              project.description || '',
              ...(project.topics || []),
              ...(project.integrations || []),
            ]
              .join(' ')
              .toLowerCase()

            const matchedTokens = tokens.filter((tok) => searchable.includes(tok))
            return {
              project_id: project.project_id,
              full_name: project.full_name,
              description: project.description,
              tier: project.tier,
              track: project.track,
              matched_keywords: matchedTokens,
              score: matchedTokens.length,
            }
          })

          const topMatches = scored
            .filter((item) => item.score > 0)
            .sort((a, b) => b.score - a.score)
            .slice(0, 5)

          const payload = {
            query_idea: text,
            extracted_keywords: tokens,
            matched_count: topMatches.length,
            closest_projects: topMatches,
            generated_at: res.generated_at,
          }
          return {
            content: [{ type: 'text', text: JSON.stringify(payload, null, 2) }],
          }
        }

        case 'methodology': {
          const methodologyDoc = {
            title: 'HackProof Evidence Methodology',
            purpose: 'Reconstruct HackMeridian 2026 hackathon submissions directly from Stellar testnet ledger data and GitHub repository matches.',
            hack_window: {
              start: '2026-10-17T09:00:00Z',
              end: '2026-10-18T12:00:00Z',
              duration: '27 hours',
            },
            evidence_tiers: {
              verified: 'Exact match between on-chain contract deploy/invocation and git repository activity inside the hack window.',
              likely: 'Repository created or modified during the hack with Stellar SDK dependencies and at least 5 commits inside the window.',
              possible: 'Activity detected with weak attribution or single matching commit.',
              unattributed: 'On-chain deployer accounts with activity during the hack window but no matching public repository discovered.',
            },
            reproducibility: 'All data is rebuilt deterministically from public Horizon & Soroban RPC and public GitHub repositories.',
            generated_at: new Date().toISOString(),
          }
          return {
            content: [{ type: 'text', text: JSON.stringify(methodologyDoc, null, 2) }],
          }
        }

        default:
          return {
            isError: true,
            content: [{ type: 'text', text: `Unknown tool: ${name}` }],
          }
      }
    } catch (error: any) {
      return {
        isError: true,
        content: [{ type: 'text', text: `Error executing ${name}: ${error.message || String(error)}` }],
      }
    }
  })

  return server
}
