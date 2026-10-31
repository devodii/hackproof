# hackproof-mcp

Model Context Protocol (MCP) server for [HackProof](https://github.com/devodii/hackproof) — inspect, query, and verify HackMeridian 2026 hackathon projects, contracts, and deployments rebuilt from Stellar testnet ledger activity.

## Features & Tools

- `list_hackathons`: List indexed hackathons and verification windows.
- `get_summary`: High-level aggregate metrics (projects, contracts, builders, freshness timestamp).
- `query_projects`: Search projects by keywords, evidence tier, track, or integration partner.
- `get_project`: Full project breakdown including contracts, wasm uploads, and evidence links.
- `get_contract`: Detailed contract deployment record on Stellar testnet.
- `hourly`: 27-hour window contract deployment timeline.
- `distributions`: Geographic countries and tier distributions.
- `top_errors`: Most frequent transaction failure codes and error kinds.
- `compare_idea(text)`: Semantic keyword similarity matcher against all submissions.
- `methodology()`: Official evidence tier definitions and attribution rules.

Every tool response includes a `generated_at` timestamp indicating data freshness. Responses are cached with an in-memory TTL and support ETag revalidation.

---

## Installation & Running

You can run the MCP server directly using `npx`:

```sh
npx hackproof-mcp
```

Or run locally within the HackProof repository:

```sh
cd apps/mcp
pnpm build
pnpm start
```

---

## Configuration

### Claude Desktop

Add this to your `claude_desktop_config.json`:

- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux:** `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "hackproof": {
      "command": "npx",
      "args": ["-y", "hackproof-mcp"],
      "env": {
        "HACKPROOF_API_URL": "https://hackproof.vercel.app/api"
      }
    }
  }
}
```

### Cursor

Add to your project's `.cursor/mcp.json` or global Cursor settings:

```json
{
  "mcpServers": {
    "hackproof": {
      "command": "npx",
      "args": ["-y", "hackproof-mcp"],
      "env": {
        "HACKPROOF_API_URL": "https://hackproof.vercel.app/api"
      }
    }
  }
}
```

### Raven

Add to your `raven.json` MCP configuration:

```json
{
  "servers": [
    {
      "name": "hackproof",
      "transport": "stdio",
      "command": "npx",
      "args": ["-y", "hackproof-mcp"],
      "env": {
        "HACKPROOF_API_URL": "https://hackproof.vercel.app/api"
      }
    }
  ]
}
```

---

## Development & Tests

```sh
cd apps/mcp
pnpm install
pnpm build
pnpm test
```
