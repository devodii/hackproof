# hackproof

HackMeridian 2026 submissions, rebuilt from the chain. No public list exists, so hackproof reads Stellar testnet for every contract deploy, wasm upload, classic operation and failed transaction in the hack window, finds the GitHub repos behind them, and links the two with exact, explainable matches. You can browse the projects, check every claim on Stellar Expert and GitHub, download the data, and ask questions in a chat that queries it.

## How it works

The official list is private, so this is a best-effort reconstruction. The window is 2026-10-25T09:00Z to 2026-10-26T12:00Z (27 hours), set in `config/hackmeridian-2026.yaml`.

**Chain.** Soroban RPC gives every contract deploy and wasm upload, the accounts funded by friendbot, classic operations, new assets and failed Soroban transactions.

**GitHub.** Searches are sliced until each fits under the 1,000 result cap: repositories by push time, code by file size. Candidates with commits in the window are scanned for contract ids, accounts, assets and wasm hashes (all checksum validated), Stellar dependencies, and the manifests as they were before the window, to catch projects that added Stellar during it.

**Linking.** Links are exact matches, never fuzzy names. Each records its method, strongest first:

| Method | Meaning |
| --- | --- |
| `contract_in_repo` | a deployed contract id appears in the repo |
| `wasm_hash_match` | a committed wasm has the hash of an uploaded wasm |
| `wasm_meta` | the deployed wasm names the repo in its metadata |
| `asset_in_repo` | an asset issued in the window appears in the repo |
| `deployer_in_repo` | a deploying account appears in the repo |
| `footprint` | derived: one linked key pulls in that account's other contracts |

Accounts that appear in more than eight repos are treated as shared infrastructure and ignored. When several repos link the same item, the strongest method wins, then the earliest repo. No language model is used in any join.

**Tiers.** Each project has one evidence tier, and the site lists the first two.

- `verified`: an exact repo to chain match, with chain activity in the window.
- `likely`: a Stellar dependency and commits in the window, and the repo was created or added Stellar during it. A signal, not proof.
- `possible`: a Stellar dependency and at least three commits in the window.

Each exported project also has a `track`, inferred from history: `genesis` if the repo was created in the window, `scale` if it is older. Teams were not asked which track they entered.

**Verify it yourself.** Every id links to Stellar Expert, every match names the repo file it was found in, and commit counts link to the filtered history. The exports in `apps/web/public/data` carry the same links and validate against the JSON Schema next to them.

**What still escapes.** Private repos, throwaway keys never committed, Futurenet and local builds, and mainnet-only teams unless the repo names the network. The official total is not public, so no share of it is claimed. Only public data is used, and emails are never collected.

## Ask the data

A prompt docked at the bottom of every page opens a full screen chat. Replies stream from `POST /api/chat`, where Claude answers using tools over the same queries as the site, and can search the web for event details. On a project or builder page it already knows which one you are looking at. Messages are limited to 10 a minute and 50 an hour per client, and history stays in the browser. The prompts live in `apps/api/src/hackproof/chat/system-prompt.md`.

## Layout

- `apps/web`: React, Vite and shadcn/ui
- `apps/api`: FastAPI, asyncpg and Postgres, managed with uv
- `config/hackmeridian-2026.yaml`: the window and the discovery queries

## Run it

```sh
cp .env.example .env
docker compose up -d db
pnpm install
pnpm dev:api
pnpm dev:web
```

The web app is on `localhost:5173` and proxies `/api` to the API on port 8000. `docker compose up` runs the whole stack in containers instead. Set `ANTHROPIC_API_KEY` to enable the chat.

## Build the data

The pipeline is four idempotent steps plus an export. Run them from `apps/api`, or as `docker compose run --rm cli <step>`.

```sh
uv run hackproof sync       # chain: deploys, uploads, classic ops, fundings, failures
uv run hackproof discover   # github: candidate repos from searches and dependency queries
uv run hackproof scan       # github: scan repos for contract ids, accounts, assets, wasm hashes
uv run hackproof reconcile  # join chain and github into links and projects
uv run hackproof export     # write the JSON and YAML exports and their schema
```

`discover` and `scan` need `HACKPROOF_GITHUB_TOKEN`. Several comma separated tokens are rotated.

## Deploy

The API ships as a Docker image (`apps/api/Dockerfile`) and runs on Railway. It reads `DATABASE_URL` (any Postgres), `ANTHROPIC_API_KEY` for the chat and `HACKPROOF_CORS_ORIGINS`, a JSON list of the web origins. Pushes to `main` that touch `apps/api` deploy automatically once the `RAILWAY_TOKEN` repository secret holds a Railway project token.

Host the web app anywhere static and build it with `VITE_API_URL` set to the API's public url.

## Checks

```sh
cd apps/api && uv run ruff check . && uv run ruff format --check . && uv run pytest
pnpm lint && pnpm format:check && pnpm build
```
