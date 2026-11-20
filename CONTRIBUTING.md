# Contributing to HackProof

Thanks for helping. Pick an issue, say so in a comment, and open one pull request per issue. Issues labeled `good first issue` are the best place to start.

## Layout

- `apps/api`: FastAPI, asyncpg and Postgres, managed with uv. Source is in `apps/api/src/hackproof`
  - `indexer/`: reads the hack window from Horizon and Soroban RPC into Postgres
  - `github/`: discovers and scans candidate repos
  - `linking/`: links repos to chain activity and builds the `projects` table
  - `export/`: writes the public JSON and YAML dataset and its schema
  - `chat/`: the chat endpoint and its tools
  - `queries.py`, `routes.py`, `schemas.py`: the public API
- `apps/web`: React, Vite and shadcn/ui
- `data`: one YAML per hackathon (`hackmeridian-2026.yaml`), `integrations.yaml`, and one folder of project files per year

The README has the commands to run everything locally.

## Python

- Python 3.13, uv, ruff and pytest.
- Pydantic models for anything that crosses a module boundary. No dataclasses, NamedTuple or TypedDict.
- A response model with defaulted fields sets `json_schema_serialization_defaults_required=True` so the generated TypeScript marks them required, and uses a `Literal` for any closed set of strings.
- Models for upstream responses use `extra="allow"` so new fields are not lost. Models we derive use `extra="forbid"`.
- Tests run against the scratch Postgres database from `tests/conftest.py` and never touch the live network. Anything that needs an upstream response uses a recorded fixture in `apps/api/tests/fixtures/`.
- New pipeline steps follow the existing shape: a `run_*` job in the relevant package, a subcommand in `cli.py`, and any schema change as files in `db/schema` with a migration from `hackproof schema plan`. SQL goes in `src/hackproof/sql`, loaded with `load_sql`, never in Python strings.

## React

- Vite, TypeScript in strict mode, Tailwind and shadcn/ui.
- Types for API responses are generated from the Pydantic models. Change a model, run `pnpm types` and commit `apps/web/openapi.json` with `apps/web/src/lib/api-schema.ts`. Never write an API type by hand in `lib/types.ts`. CI fails when either file is stale.
- Add shadcn components with the shadcn CLI. Never hand edit `components/ui`.
- Reusable pieces that know nothing about hackathons go in `components/charts` or a similar neutral folder. Pages live in `pages/` and are registered in `App.tsx`.
- Fetch data through `lib/api.ts` and a hook in `hooks/` built on TanStack Query.
- Comments only where they explain something non-obvious.

## Data and privacy

- The public dataset contains GitHub handles and public profile fields only.
- Never store or publish emails, private messages or anything that is not on a public profile.
- Locations are only ever the text the user wrote on their public profile, normalized to a country.
- A new column or table that appears in the export means a new export schema version. Keep the old schema files.
- Production does not run the scans, so whatever the scans find reaches it from the committed project files through `hackproof import`, which CI runs on merge and the data sync runs before it exports. A new section on the project files must be added to `RESTORED` in `export/restore.py`, or to `FROM_DATABASE` when the database can rebuild it. A test fails until you do, and without it the sync would open a pull request that deletes the section.

## Checks

Run these before you open a pull request:

```sh
cd apps/api && uv run ruff check . && uv run ruff format --check . && uv run pytest
pnpm lint && pnpm format:check && pnpm build
```

## Commits and pull requests

- Commit messages are `type: subject`, for example `feat: add the stellar expert client`. Use lowercase, the imperative mood and no scope.
- Keep commits small and focused.
- Link the issue in the pull request description.
- Include screenshots for anything visual.
