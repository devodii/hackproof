#!/usr/bin/env node

import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js'
import { createMcpServer } from './server.js'

async function main() {
  const server = createMcpServer()
  const transport = new StdioServerTransport()

  process.on('SIGINT', async () => {
    await server.close()
    process.exit(0)
  })

  process.on('SIGTERM', async () => {
    await server.close()
    process.exit(0)
  })

  await server.connect(transport)
  console.error('HackProof MCP server running on stdio')
}

main().catch((error) => {
  console.error('Fatal error in HackProof MCP server:', error)
  process.exit(1)
})
