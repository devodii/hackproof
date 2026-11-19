<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/hackmeridian-light.png">
  <img src="assets/hackmeridian-dark.png" alt="HackMeridian" width="200">
</picture>

# HackProof

HackMeridian 2026 submissions, rebuilt from Stellar testnet and linked to their GitHub repos by exact matches. Browse the projects, check each match on Stellar Expert and GitHub, download the data, or ask the chat.

Each project has an evidence tier. `verified` means an exact repo to chain match with activity in the window. `likely` (shown as "Code only") means a Stellar dependency and at least 5 commits in the window, in a repo created or updated for the event. The window is set in `data/hackmeridian-2026.yaml`.

## Layout

- `apps/web`: React, Vite and shadcn/ui
- `apps/api`: FastAPI, asyncpg and Postgres, managed with uv
- `apps/api/src/hackproof/chat/system-prompt.md`: the chat prompts
- `data`: the dataset, one YAML file per project, plus the event and integration configs. See [data/README.md](data/README.md)

## Run

```sh
cp .env.example .env
docker compose up -d db
pnpm install
pnpm dev:api
pnpm dev:web
```

The web app is on `localhost:5173` and proxies `/api` to port 8000. Set `ANTHROPIC_API_KEY` to enable the chat.

## Data

Run from `apps/api`. `discover` and `scan` need `HACKPROOF_GITHUB_TOKEN`.

```sh
uv run hackproof sync
uv run hackproof discover
uv run hackproof scan
uv run hackproof reconcile
uv run hackproof observe
uv run hackproof export
```

`observe` reads the live state of the contracts a deep integration declares, through the adapter named in its profile, and maps the hack's assets to their contract ids so the two can be compared.

## Deep integrations

Any partner or tool in `data/integrations.yaml` can carry a `profile`. It lists the partner's known contract addresses, regex signals that say how the code uses it, values to capture from source, and checks built from those signals. The scan reads more files for a repo that shows the partner and records what it finds as evidence, `/api/integrations/{slug}` and the page at `/integration/{slug}` render it for every partner the same way, and the project files carry a `profile` per integration. A profile with no `adapter` needs no code at all, as Stellar Registry shows. Set `adapter` to a class registered in `integrations/adapters` when the partner's contracts can be read live; Reflector's adapter reads each oracle feed, its assets, when each asset expires, and a live price.

## Database

The schema lives in `apps/api/db/schema`, one file per table, index, view and function, and is applied with [pgschema](https://github.com/pgplex/pgschema). Queries live in `apps/api/src/hackproof/sql`. Run from `apps/api`.

```sh
uv run hackproof schema apply
uv run hackproof schema plan
uv run hackproof schema verify
```

To change the schema, edit the files in `db/schema`, run `schema plan`, and commit the numbered file it writes to `db/migrations` with your change. `apply` refuses a plan that drops data. CI checks every pull request against an empty database and migrates production when the pull request merges to `main`.

## Checks

```sh
cd apps/api && uv run ruff check . && uv run ruff format --check . && uv run sqlfluff lint db/schema src/hackproof/sql && uv run pytest
pnpm lint && pnpm format:check && pnpm build
```
