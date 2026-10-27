# hackproof

HackMeridian submissions, rebuilt from the chain. No public list exists, so hackproof reads Stellar testnet for every contract deploy, wasm upload, classic operation and failed transaction in the hack window, finds the GitHub repos behind them, and links the two with exact, explainable matches. Builders who deployed during the hack can connect a wallet, sign once and claim a proof.

How the join works, and what it cannot see, is in [docs/METHODOLOGY.md](docs/METHODOLOGY.md).

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

The web app is on `localhost:5173` and proxies `/api` to the API on port 8000. `docker compose up` runs the whole stack in containers instead.

## Build the data

The pipeline is four idempotent steps. Run them from `apps/api`, or as `docker compose run --rm cli <step>`.

```sh
uv run hackproof sync       # chain: deploys, uploads, classic ops, fundings, failures
uv run hackproof discover   # github: candidate repos from searches and dependency queries
uv run hackproof scan       # github: scan repos for contract ids, accounts, assets, wasm hashes
uv run hackproof reconcile  # join chain and github into links and projects
```

`discover` and `scan` need `HACKPROOF_GITHUB_TOKEN`. Several comma separated tokens are rotated.

## Checks

```sh
cd apps/api && uv run ruff check . && uv run ruff format --check . && uv run pytest
pnpm lint && pnpm format:check && pnpm build
```
