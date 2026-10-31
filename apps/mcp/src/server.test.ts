import assert from 'node:assert/strict'
import test from 'node:test'

import { HackProofClient } from './client.js'
import { createMcpServer } from './server.js'

// Mock fixture client that returns recorded data without network calls
class FixtureHackProofClient extends HackProofClient {
  constructor() {
    super('http://fixture.local/api')
  }

  override async getStats() {
    return {
      data: {
        projects: 42,
        verified_projects: 20,
        likely_projects: 15,
        possible_projects: 7,
        unattributed_accounts: 10,
        contracts: 55,
        builders: 30,
        contributors: 65,
        countries: 18,
        wasm_uploads: 40,
        failed_txs: 5,
        generated_at: '2026-10-31T12:00:00Z',
      },
      generated_at: '2026-10-31T12:00:00Z',
    }
  }

  override async getTimeline() {
    return {
      data: [
        { hour: '2026-10-17T10:00:00Z', contracts: 3 },
        { hour: '2026-10-17T11:00:00Z', contracts: 12 },
      ],
      generated_at: '2026-10-31T12:00:00Z',
    }
  }

  override async getCountries() {
    return {
      data: [
        { country: 'PT', contributors: 25 },
        { country: 'BR', contributors: 14 },
      ],
      generated_at: '2026-10-31T12:00:00Z',
    }
  }

  override async getIntegrations() {
    return {
      data: [
        {
          slug: 'privy',
          name: 'Privy',
          category: 'Auth',
          site: 'https://privy.io',
          projects: 6,
        },
      ],
      generated_at: '2026-10-31T12:00:00Z',
    }
  }

  override async getProjects() {
    return {
      data: {
        total: 1,
        items: [
          {
            project_id: 'repo:stellar/soroban-vault',
            full_name: 'stellar/soroban-vault',
            url: 'https://github.com/stellar/soroban-vault',
            footprint: 'contracts' as const,
            tier: 'verified' as const,
            contracts: 4,
            classic_ops: 8,
            assets: 1,
            builders: 2,
            wasm_uploads: 3,
            failed_txs: 0,
            first_activity: '2026-10-17T10:00:00Z',
            last_activity: '2026-10-17T18:00:00Z',
            description: 'Automated yield vault and lending protocol on Soroban',
            homepage: 'https://vault.stellar.org',
            stars: 55,
            forks: 12,
            language: 'Rust',
            license: 'Apache-2.0',
            owner: 'stellar',
            owner_avatar: null,
            country: 'PT',
            window_commits: 18,
            total_commits: 22,
            stellar_added_in_window: true,
            created_at: '2026-10-17T09:30:00Z',
            topics: ['defi', 'vault', 'lending'],
            track: 'genesis' as const,
            integrations: ['privy'],
            award: 'first' as const,
          },
        ],
      },
      generated_at: '2026-10-31T12:00:00Z',
    }
  }

  override async getProject(projectId: string) {
    return {
      data: {
        project: (await this.getProjects()).data.items[0],
        links: [
          {
            subject_kind: 'contract',
            subject: 'CAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA',
            method: 'contract_in_repo',
            path: 'src/lib.rs',
          },
        ],
        integration_uses: [
          {
            slug: 'privy',
            name: 'Privy',
            method: 'package' as const,
            evidence: '@privy-io/node in package.json',
            path: 'package.json',
          },
        ],
        contributors: [
          {
            login: 'alice',
            url: 'https://github.com/alice',
            avatar_url: null,
            contributions: 14,
            country: 'PT',
          },
        ],
        contracts: [
          {
            contract_id: 'CAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA',
            deployer: 'GAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA',
            wasm_hash: '1111111111111111111111111111111111111111111111111111111111111111',
            tx_hash: '2222222222222222222222222222222222222222222222222222222222222222',
            ledger: 100,
            deployed_at: '2026-10-17T11:00:00Z',
            project_id: projectId,
          },
        ],
        wasm_uploads: [],
        failed_txs: [],
      },
      generated_at: '2026-10-31T12:00:00Z',
    }
  }

  override async getContracts() {
    return {
      data: {
        total: 1,
        items: [
          {
            contract_id: 'CAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA',
            deployer: 'GAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA',
            wasm_hash: '1111111111111111111111111111111111111111111111111111111111111111',
            tx_hash: '2222222222222222222222222222222222222222222222222222222222222222',
            ledger: 100,
            deployed_at: '2026-10-17T11:00:00Z',
            project_id: 'repo:stellar/soroban-vault',
          },
        ],
      },
      generated_at: '2026-10-31T12:00:00Z',
    }
  }

  override async getWasm() {
    return {
      data: {
        total: 1,
        items: [
          {
            wasm_hash: '1111111111111111111111111111111111111111111111111111111111111111',
            uploader: 'GAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA',
            tx_hash: '3333333333333333333333333333333333333333333333333333333333333333',
            size: 24500,
            source_repo: 'stellar/soroban-vault',
            full_name: 'stellar/soroban-vault',
            contracts: 1,
            uploaded_at: '2026-10-17T10:45:00Z',
          },
        ],
      },
      generated_at: '2026-10-31T12:00:00Z',
    }
  }

  override async getFailed() {
    return {
      data: {
        total: 1,
        items: [
          {
            tx_hash: '4444444444444444444444444444444444444444444444444444444444444444',
            source_account: 'GAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA',
            kind: 'invokeHostFunction',
            result_code: 'txFAILED',
            ledger: 101,
            created_at: '2026-10-17T11:05:00Z',
          },
        ],
      },
      generated_at: '2026-10-31T12:00:00Z',
    }
  }
}

test('MCP Server lists all 10 tools', async () => {
  const client = new FixtureHackProofClient()
  const server = createMcpServer(client)

  const handlers = (server as any)._requestHandlers
  assert.ok(handlers.has('tools/list'))
  assert.ok(handlers.has('tools/call'))
})

test('Every MCP tool returns valid data with fixture API', async () => {
  const client = new FixtureHackProofClient()
  const server = createMcpServer(client)
  const callHandler = (server as any)._requestHandlers.get('tools/call')

  // Helper to call tool through Zod-compliant request shape
  const callTool = async (name: string, args: Record<string, any> = {}) => {
    return callHandler({
      method: 'tools/call',
      params: { name, arguments: args },
    })
  }

  // 1. list_hackathons
  const res1 = await callTool('list_hackathons')
  assert.strictEqual(res1.isError, undefined)
  const data1 = JSON.parse(res1.content[0].text)
  assert.strictEqual(data1.hackathons[0].slug, 'hackmeridian-2026')
  assert.ok(data1.generated_at)

  // 2. get_summary
  const res2 = await callTool('get_summary')
  assert.strictEqual(res2.isError, undefined)
  const data2 = JSON.parse(res2.content[0].text)
  assert.strictEqual(data2.data.projects, 42)
  assert.ok(data2.generated_at)

  // 3. query_projects
  const res3 = await callTool('query_projects', { q: 'vault' })
  assert.strictEqual(res3.isError, undefined)
  const data3 = JSON.parse(res3.content[0].text)
  assert.strictEqual(data3.count, 1)
  assert.ok(data3.generated_at)

  // 4. get_project
  const res4 = await callTool('get_project', { project_id: 'stellar/soroban-vault' })
  assert.strictEqual(res4.isError, undefined)
  const data4 = JSON.parse(res4.content[0].text)
  assert.strictEqual(data4.data.project.project_id, 'repo:stellar/soroban-vault')
  assert.strictEqual(data4.data.links.length, 1)

  // 5. get_contract
  const res5 = await callTool('get_contract', { contract_id: 'CAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA' })
  assert.strictEqual(res5.isError, undefined)
  const data5 = JSON.parse(res5.content[0].text)
  assert.strictEqual(data5.matched_contracts.length, 1)

  // 6. hourly
  const res6 = await callTool('hourly')
  assert.strictEqual(res6.isError, undefined)
  const data6 = JSON.parse(res6.content[0].text)
  assert.strictEqual(data6.timeline.length, 2)
  assert.strictEqual(data6.peak_hour.contracts, 12)

  // 7. distributions
  const res7 = await callTool('distributions')
  assert.strictEqual(res7.isError, undefined)
  const data7 = JSON.parse(res7.content[0].text)
  assert.strictEqual(data7.countries.length, 2)
  assert.strictEqual(data7.tiers.verified, 20)

  // 8. top_errors
  const res8 = await callTool('top_errors', { limit: 10 })
  assert.strictEqual(res8.isError, undefined)
  const data8 = JSON.parse(res8.content[0].text)
  assert.strictEqual(data8.total_failed_txs_sampled, 1)
  assert.strictEqual(data8.top_result_codes[0].code, 'txFAILED')

  // 9. compare_idea
  const res9 = await callTool('compare_idea', { text: 'A lending vault protocol for soroban' })
  assert.strictEqual(res9.isError, undefined)
  const data9 = JSON.parse(res9.content[0].text)
  assert.strictEqual(data9.matched_count, 1)
  assert.ok(data9.closest_projects[0].matched_keywords.includes('vault'))

  // 10. methodology
  const res10 = await callTool('methodology')
  assert.strictEqual(res10.isError, undefined)
  const data10 = JSON.parse(res10.content[0].text)
  assert.strictEqual(data10.hack_window.duration, '27 hours')
  assert.ok(data10.evidence_tiers.verified)
})
