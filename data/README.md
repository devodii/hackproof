# Data

The HackProof dataset: one YAML file per project, plus the config that produces it.

## Layout

```
data/
  hackmeridian-2026.yaml         event config: window, awards, discovery queries
  integrations.yaml              Stellar integration partners and how each is detected
  schema-hackathon-project.yml   JSON Schema for every project file, generated
  2026/<project>.yml             one file per HackMeridian 2026 project
```

A new event adds `data/hackmeridian-2027.yaml`. Point `HACKPROOF_HACKATHON_FILE` at it, run the
pipeline, and `export` creates `data/2027/`. Nothing else changes.

## Generating

From `apps/api`:

```sh
uv run hackproof export
```

This rewrites every project file for the event year, deletes files of projects that are gone, and
rewrites the schema from the same models. Do not edit the project files by hand.

## Publishing

The site publishes this folder at `/data` on every build:

- `/data/2026/<project>.yml`
- `/data/schema-hackathon-project.yml`
- `/data/hackmeridian-2026/projects.json` and `projects.yml`: the whole year in one file, built from
  `data/2026` so links shared earlier keep working. The project fields follow the project files, not
  the old export.

## File names

`<project>` is the repo name lowercased, with every run of characters outside `[a-z0-9]` replaced by
one `-` (`Stellar-Split` becomes `stellar-split`). When projects in a year share a name, each gets
its owner as a prefix, `<owner>-<name>`. A clash left after that stops the export.

## Fields

| Field | Meaning |
| --- | --- |
| `event` | Event slug, for example `hackmeridian-2026` |
| `canonical_id` | `pkg:github/<owner>/<repo>`, the join key into other repo datasets |
| `repo_url`, `name`, `owner` | Repo URL, repo name and owner login |
| `description`, `homepage`, `language`, `license` | Repo metadata, left out when unknown |
| `topics` | Tags the team set on the repo, left out when none |
| `created_at` | Repo creation time, UTC |
| `track` | `genesis` or `scale` |
| `track_declared` | See below |
| `award` | `first` or `runner-up`, left out when none |
| `evidence_tier` | See below |
| `commits_in_window` | Commits made during the event window |
| `stack` | Stellar package to declared version, `null` when the manifest gives none |
| `integrations` | Ecosystem partners found, each with `evidence` (`method` is `package` or `endpoint`, `detail`, `file_url`) |
| `chain` | Testnet counts, the attributed `accounts` and the `evidence` behind the tier. Both lists are always present |
| `contributors` | Public GitHub `login` and `contributions`. Always present |

Stars, forks, total commits, last commit time, avatars and countries are not included. They change
often or are personal.

### `evidence_tier`

- `verified`: the repo matches on-chain activity exactly (a deployer, contract or asset found in the
  repo), and that account was active on chain inside the event window.
- `likely`: shown on the site as "Code only". The repo looks like a submission but has no on-chain
  proof.

### `track_declared`

`true` only when the team states its track in its own docs, and `track` is then that value. `false`
means the team did not say, and `track` is the default `genesis`, an assumption and not a fact.

## Privacy

Public GitHub handles and public repo facts only. No emails, avatars, locations or other personal
data.
