# Methodology

HackProof reconstructs the HackMeridian 2026 submission list from public traces. The official list is private, so this is a best-effort reconstruction, and it prints how complete it is.

## The window

Official start is 2026-10-25T09:00:00Z and the submission deadline is 2026-10-26T12:00:00Z, which is 27 hours. Portugal left summer time at 01:00Z on 25 October, so Lisbon time equals UTC that morning. The hackmeridian.com structured data still says `+01:00`, so the pull starts one hour early at 08:00Z. Everything is configured in `config/hackmeridian-2026.yaml`.

## Chain fingerprints

Read from Soroban RPC for every ledger in the window:

- **Soroban deploys:** wasm uploads and contract creations. Each gives a deployer, a contract id and a wasm hash. The contract id is derived from the deploy preimage and checked against the chain.
- **Hacker accounts:** every account created by the testnet friendbot inside the window.
- **Classic operations:** payments, path payments, trustlines, offers, data entries, options, claimable balances and liquidity pool operations. A project with no contract lives entirely here.
- **New assets:** any `CODE:ISSUER` seen in those operations whose issuer is a hacker or deployer account.
- **Failed Soroban transactions:** kept with their result code.

## GitHub fingerprints

GitHub caps every search at 1,000 results, so each query is sliced until every slice fits: repository searches by push time, code searches by file size. Candidates are then looked up in bulk through the GraphQL API.

- Repository search by name, description, readme and topic (`stellar`, `soroban`, `hackmeridian`, `lisbon stellar` and similar), restricted to repos pushed since 24 October.
- Code search for Stellar dependencies and endpoints (`soroban-sdk`, `@stellar/stellar-sdk`, wallet kits, the testnet passphrase, friendbot and RPC hosts). Code search has no date filter, so hits are kept only when the repo was pushed since 24 October.
- Repos named in the `source_repo` entry of a deployed wasm's contract metadata.

A candidate is only scanned in depth if it has at least one commit inside the window, or was named in wasm metadata. The scan then records:

- Contract ids, account ids, `CODE:ISSUER` assets and network markers found in text files up to 512 kB, all checked against Stellar checksums.
- The sha256 of committed `.wasm` files.
- Dependency manifests (Rust, JS, Python, Go) fingerprinted for Stellar packages.
- Commits inside the window.
- **Dependency history:** the manifests as they were at the last commit before the window are compared with today's. A Stellar package that was absent then and present now was added during the hack, which catches existing projects that built a Stellar integration for the event. A repo with no commit before the window was born inside it.
- The demo site bundle, when a demo url is known, searched for the same ids.

## Linking

Links are exact matches, never fuzzy name matching. Each link records the method that produced it, listed here strongest first:

| Method | Meaning |
| --- | --- |
| `contract_in_repo` | a deployed contract id appears in the repo |
| `wasm_hash_match` | a wasm committed to the repo has the hash of an uploaded wasm |
| `wasm_meta` | the deployed wasm names the repo in its contract metadata |
| `asset_in_repo` | an asset issued inside the window appears in the repo |
| `deployer_in_repo` | a hacker or deployer account appears in the repo |
| `footprint` | derived: one linked key pulls in the rest of that account's contracts and assets |

Accounts that appear in more than eight repos are treated as shared infrastructure and ignored. Footprint expansion through a wasm only happens when a single account uploaded that wasm, so a shared template does not merge unrelated teams. When several repos link the same item, the strongest method wins, then the earliest-created repo.

## Projects

A project is a repo with at least one link, a wasm-metadata repo, or a repo with a Stellar dependency that also shows hackathon activity: several commits in the window, creation in the window, or a Stellar dependency added during the window. Chain activity with no repo stays visible as an unattributed account project.

Each project gets one evidence tier:

- **Verified:** an exact repo to chain match, with chain activity inside the window.
- **Likely:** a Stellar dependency and commits in the window, and the repo was created in the window or added Stellar during it. A signal, not proof.
- **Possible:** a Stellar dependency and at least three commits in the window, nothing else.

The site lists verified and likely projects.

Each exported project also carries the track it fits, inferred from its history: **genesis** for a product created during the hack, **scale** for an existing product that predates it. Teams were not asked which track they entered, so this is an inference.

No language model is used in any join.

## Verify it yourself

Every identifier on the site links to the place you can check it.

- Contracts, accounts, transactions, ledgers and assets open on [Stellar Expert](https://stellar.expert/explorer/testnet) for testnet.
- Each project's evidence table names the repo file a match was found in and links to it on GitHub.
- Commit counts link to the repo's commit history filtered to the 27 hour window.
- Contributors and owners link to their GitHub profiles, and demos link to the project's own site.
- The exported JSON and YAML carry the same Stellar Expert and GitHub urls for every item.

To check a verified project: open it, follow a matched contract to Stellar Expert and confirm it was deployed inside the window, then follow the "Found in" link and confirm the contract id is in that file. Tiers below verified are signals, and the site labels them that way.

## What still escapes

Private repos. Teams that used a throwaway key they never committed and never posted a repo for. Futurenet and local-only builds. Mainnet-only teams are only noticed when their repo names the network. Team grouping by accounts that fund each other, and rebuilding contracts from source to compare hashes, are not implemented yet.

The home page prints how many projects were found. The official total is not public, so no percentage of the true total is claimed.

## Privacy

Only public data is used: chain activity and public GitHub repos and profile fields. Handles are shown, emails are not collected or displayed.

## Reproducing

```sh
docker compose up -d db
cd apps/api
uv run hackproof sync
uv run hackproof discover
uv run hackproof scan
uv run hackproof reconcile
```
