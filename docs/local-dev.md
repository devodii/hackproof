# Local Development

A fresh clone can start Postgres, seed anonymized sample data (10 projects, 20 contracts, and the full 27-hour event series), and launch the API and web UI without a GitHub token or a live Stellar testnet sync.

## Five Commands to a Running UI

```sh
git clone https://github.com/devodii/hackproof.git
cd hackproof
cp .env.example .env
docker compose up -d
open http://localhost:5173
```

When `docker compose up -d` runs:

1. `db` starts Postgres 17 and waits until `pg_isready` passes.
2. `seed` runs `uv run hackproof seed` once, creating the schema and loading `data/sample/sample.sql` if and only if the `projects` table is empty.
3. `api` starts FastAPI on `http://localhost:8000`.
4. `web` starts Vite on `http://localhost:5173` and proxies `/api` to `api:8000`.

## Running Outside Docker

If you prefer running the API and web app directly on your host with only Postgres in Docker:

```sh
cp .env.example .env
docker compose up -d db
cd apps/api && uv run hackproof seed && cd ../..
pnpm install
pnpm dev:api & pnpm dev:web
```

## Regenerating the Sample Dataset

To regenerate `data/sample/sample.sql` from your local development database (automatically stripping any avatar URLs, locations, or country fields so only public GitHub handles and public chain facts remain):

```sh
cd apps/api && uv run hackproof dump-sample
```
