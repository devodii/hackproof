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
- `data`: the dataset, one YAML file per project, plus one config per hackathon and the shared integrations. See [data/README.md](data/README.md)

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
uv run hackproof run
```

`run` does the whole job for one hackathon, in order: `sync` indexes the hack window from the chain, `discover` finds candidate repos, `scan` reads them, `reconcile` links chain activity to repos and builds the projects, `observe` reads the live state of the integrations' contracts, and `export` writes the project files into `data`. It stops at the first stage that fails and prints the command to carry on from there. Use `--from reconcile`, `--only export` or `--skip discover scan` to run part of it, and `--force`, `--projects` or `--strings` to change how the scan and discovery behave. The stages are also commands of their own.

To run a new hackathon, copy `data/hackmeridian-2026`, set the slug in `main.yaml`, window, awards and discovery queries, create a database for it and run:

```sh
HACKPROOF_DATABASE_URL=postgresql://... uv run hackproof schema apply
HACKPROOF_DATABASE_URL=postgresql://... uv run hackproof run --hackathon ../../data/<id>/main.yaml
```

The tables are not split by event, so each hackathon gets a database of its own, and `run` records the event in the database and refuses to run another one on it. Against a database that is not on this machine it needs `--remote`.

`observe` reads the live state of the contracts a deep integration declares, through the adapter named in its profile, and maps the hack's assets to their contract ids so the two can be compared.

## Deep integrations

Any partner or tool in `data/integrations.yaml` can carry a `profile`. It lists the partner's known contract addresses, regex signals that say how the code uses it, values to capture from source, and checks built from those signals. The scan reads more files for a repo that shows the partner and records what it finds as evidence, `/api/integrations/{slug}` and the page at `/integration/{slug}` render it for every partner the same way, and the project files carry a `profile` per integration. A profile with no `adapter` needs no code at all, as Stellar Registry shows. Set `adapter` to a class registered in `integrations/adapters` when the partner's contracts can be read live; Reflector's adapter reads each oracle feed, its assets, when each asset expires, and a live price.

A profile can also list `surfaces`: things the adapter watches that the repos never reference, such as a REST API, an npm package, a GitHub repo or a contract code hash. The adapter decides what each `kind` means and returns plain facts, and the page shows them as live cards without knowing the partner. `hints` tell the scan which paths to read first, and a check can `require` signals, need one of `missing` or fail on any of `forbids`. Trustless Work is the example: its adapter reads the published OpenAPI of three API hosts, npm, GitHub and the ledger.

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

The web app's API types are generated. After changing a response model run `pnpm types` and commit `apps/web/openapi.json` and `apps/web/src/lib/api-schema.ts`; CI fails when they are stale.
