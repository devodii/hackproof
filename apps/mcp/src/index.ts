#!/usr/bin/env node
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";

const API_BASE = process.env.HACKPROOF_API_BASE ?? "https://api.hackproof.dev";
const CACHE_TTL_MS = 60_000;

interface CacheEntry {
  data: unknown;
  etag?: string;
  fetchedAt: number;
}

const cache = new Map<string, CacheEntry>();

async function fetchJson(path: string): Promise<unknown> {
  const url = `${API_BASE}${path}`;
  const now = Date.now();
  const entry = cache.get(url);
  if (entry && now - entry.fetchedAt < CACHE_TTL_MS) {
    return entry.data;
  }

  const headers: Record<string, string> = {};
  if (entry?.etag) headers["If-None-Match"] = entry.etag;

  const res = await fetch(url, { headers });
  if (res.status === 304 && entry) {
    entry.fetchedAt = now;
    return entry.data;
  }
  if (!res.ok) {
    throw new Error(`HackProof API ${res.status} on ${path}`);
  }
  const data = await res.json();
  cache.set(url, {
    data,
    etag: res.headers.get("etag") ?? undefined,
    fetchedAt: now,
  });
  return data;
}

function withFreshness(payload: unknown, generatedAt?: string): unknown {
  const stamp = generatedAt ?? new Date().toISOString();
  if (payload && typeof payload === "object" && !Array.isArray(payload)) {
    return { ...(payload as Record<string, unknown>), generated_at: stamp };
  }
  return { data: payload, generated_at: stamp };
}

const tools = [
  { name: "list_hackathons", description: "List all hackathons tracked by HackProof.", inputSchema: { type: "object", properties: {} } },
  { name: "get_summary", description: "Get aggregate summary statistics.", inputSchema: { type: "object", properties: {} } },
  { name: "query_projects", description: "Query projects with optional filters.", inputSchema: { type: "object", properties: { q: { type: "string" }, hackathon: { type: "string" }, limit: { type: "number" } } } },
  { name: "get_project", description: "Get a single project by id.", inputSchema: { type: "object", properties: { id: { type: "string" } }, required: ["id"] } },
  { name: "get_contract", description: "Get contract details for a project.", inputSchema: { type: "object", properties: { id: { type: "string" } }, required: ["id"] } },
  { name: "hourly", description: "Hourly activity breakdown.", inputSchema: { type: "object", properties: {} } },
  { name: "distributions", description: "Distribution statistics.", inputSchema: { type: "object", properties: {} } },
  { name: "top_errors", description: "Top errors across projects.", inputSchema: { type: "object", properties: {} } },
  { name: "compare_idea", description: "Compare an idea against existing projects by keyword match.", inputSchema: { type: "object", properties: { text: { type: "string" } }, required: ["text"] } },
  { name: "methodology", description: "Explain HackProof methodology.", inputSchema: { type: "object", properties: {} } },
];

const server = new Server(
  { name: "hackproof-mcp", version: "0.1.0" },
  { capabilities: { tools: {} } }
);

server.setRequestHandler(ListToolsRequestSchema, async () => ({ tools }));

server.setRequestHandler(CallToolRequestSchema, async (req) => {
  const { name, arguments: args = {} } = req.params;
  try {
    let data: unknown;
    let generatedAt: string | undefined;
    switch (name) {
      case "list_hackathons":
        data = await fetchJson("/hackathons");
        break;
      case "get_summary": {
        const s = (await fetchJson("/stats")) as Record<string, unknown>;
        generatedAt = (s?.generated_at as string) ?? (s?.last_sync as string);
        data = s;
        break;
      }
      case "query_projects": {
        const params = new URLSearchParams();
        if (args.q) params.set("q", String(args.q));
        if (args.hackathon) params.set("hackathon", String(args.hackathon));
        if (args.limit) params.set("limit", String(args.limit));
        data = await fetchJson(`/projects?${params.toString()}`);
        break;
      }
      case "get_project":
        data = await fetchJson(`/projects/${args.id}`);
        break;
      case "get_contract":
        data = await fetchJson(`/projects/${args.id}/contract`);
        break;
      case "hourly":
        data = await fetchJson("/hourly");
        break;
      case "distributions":
        data = await fetchJson("/distributions");
        break;
      case "top_errors":
        data = await fetchJson("/top_errors");
        break;
      case "compare_idea": {
        const projects = (await fetchJson("/projects")) as Array<Record<string, unknown>>;
        const terms = String(args.text).toLowerCase().split(/\s+/).filter(Boolean);
        const scored = projects
          .map((p) => {
            const haystack = `${p.name ?? ""} ${p.description ?? ""} ${(p.topics as string[] | undefined)?.join(" ") ?? ""}`.toLowerCase();
            const matched = terms.filter((t) => haystack.includes(t));
            return { project: p, score: matched.length, matched };
          })
          .filter((s) => s.score > 0)
          .sort((a, b) => b.score - a.score)
          .slice(0, 10);
        data = { matches: scored };
        break;
      }
      case "methodology":
        data = await fetchJson("/methodology");
        break;
      default:
        throw new Error(`Unknown tool: ${name}`);
    }
    const payload = withFreshness(data, generatedAt);
    return { content: [{ type: "text", text: JSON.stringify(payload, null, 2) }] };
  } catch (err) {
    return { content: [{ type: "text", text: `Error: ${(err as Error).message}` }], isError: true };
  }
});

const transport = new StdioServerTransport();
await server.connect(transport);