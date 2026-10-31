from collections import Counter
from datetime import datetime
from typing import Any, Literal

from hackproof.db import pool
from hackproof.hackathon import get_hackathon, hidden_ids, places
from hackproof.integrations.catalog import get_catalog
from hackproof.linking.methods import METHOD_RANK_SQL

PROJECTS_SQL = """
SELECT p.project_id, p.full_name, r.url, p.footprint, p.tier, p.contracts, p.classic_ops, p.assets,
       p.builders, p.wasm_uploads, p.failed_txs, p.first_activity, p.last_activity,
       r.description, r.homepage, r.stars, r.forks, r.language, r.license, r.owner, r.owner_avatar,
       r.country, r.dependencies,
       r.window_commits, r.total_commits, r.stellar_added_in_window,
       r.created_at, r.topics, COALESCE(r.declared_track, 'genesis') AS track,
       ARRAY(SELECT i.partner FROM repo_integrations i WHERE i.full_name = p.full_name
             GROUP BY i.partner ORDER BY i.partner) AS integrations,
       count(*) OVER () AS total
FROM projects p
LEFT JOIN repos r ON r.full_name = p.full_name
WHERE ($1::text IS NULL
       OR p.project_id ILIKE '%' || $1 || '%'
       OR r.description ILIKE '%' || $1 || '%')
  AND ($2::text IS NULL
       OR p.project_id = 'acct:' || $2
       OR p.project_id IN (SELECT project_id FROM account_projects WHERE account = $2))
  AND ($3::text IS NULL OR p.project_id = $3)
  AND ($4::text[] IS NULL OR p.tier = ANY($4))
  AND ($7::text IS NULL OR COALESCE(r.declared_track, 'genesis') = $7)
  AND ($8::text[] IS NULL OR EXISTS (
       SELECT 1 FROM repo_integrations i
       WHERE i.full_name = p.full_name AND i.partner = ANY($8)))
  AND ($9::text[] IS NULL OR p.project_id = ANY($9))
ORDER BY array_position(
             ARRAY['verified', 'likely', 'possible', 'unattributed'], p.tier),
         p.contracts DESC, p.classic_ops DESC, r.stars DESC NULLS LAST, p.last_activity DESC
LIMIT $5 OFFSET $6
"""

CONTRACTS_SQL = """
SELECT c.contract_id, c.deployer, c.wasm_hash, c.tx_hash, c.ledger, c.deployed_at,
       COALESCE('repo:' || a.full_name, 'acct:' || c.deployer) AS project_id,
       count(*) OVER () AS total
FROM contracts c
LEFT JOIN attribution a ON a.subject_kind = 'contract' AND a.subject = c.contract_id
WHERE c.deployed_at BETWEEN $1 AND $2
  AND ($3::text IS NULL
       OR c.contract_id ILIKE '%' || $3 || '%'
       OR c.deployer ILIKE '%' || $3 || '%'
       OR c.wasm_hash ILIKE '%' || $3 || '%')
  AND ($4::text IS NULL OR c.deployer = $4)
  AND ($5::text IS NULL OR COALESCE('repo:' || a.full_name, 'acct:' || c.deployer) = $5)
ORDER BY c.deployed_at DESC
LIMIT $6 OFFSET $7
"""

WASM_SQL = """
SELECT w.wasm_hash, w.uploader, w.tx_hash, w.size, w.source_repo, w.uploaded_at,
       COALESCE(aa.full_name, aw.full_name) AS full_name,
       (SELECT count(*) FROM contracts c WHERE c.wasm_hash = w.wasm_hash) AS contracts,
       count(*) OVER () AS total
FROM wasm_uploads w
LEFT JOIN attribution aa ON aa.subject_kind = 'account' AND aa.subject = w.uploader
LEFT JOIN attribution aw ON aw.subject_kind = 'wasm' AND aw.subject = w.wasm_hash
WHERE w.uploaded_at BETWEEN $1 AND $2
  AND ($3::text IS NULL
       OR w.wasm_hash ILIKE '%' || $3 || '%'
       OR w.uploader ILIKE '%' || $3 || '%'
       OR w.source_repo ILIKE '%' || $3 || '%')
  AND ($4::text IS NULL OR w.uploader = $4)
  AND ($5::text IS NULL
       OR COALESCE('repo:' || COALESCE(aa.full_name, aw.full_name), 'acct:' || w.uploader) = $5)
ORDER BY w.uploaded_at DESC
LIMIT $6 OFFSET $7
"""

FAILED_SQL = """
SELECT f.tx_hash, f.source_account, f.kind, f.result_code, f.ledger, f.created_at,
       count(*) OVER () AS total
FROM failed_txs f
LEFT JOIN account_projects ap ON ap.account = f.source_account
WHERE f.created_at BETWEEN $1 AND $2
  AND ($3::text IS NULL
       OR f.tx_hash ILIKE '%' || $3 || '%'
       OR f.source_account ILIKE '%' || $3 || '%'
       OR f.result_code ILIKE '%' || $3 || '%')
  AND ($4::text IS NULL OR f.source_account = $4)
  AND ($5::text IS NULL OR COALESCE(ap.project_id, 'acct:' || f.source_account) = $5)
ORDER BY f.created_at DESC
LIMIT $6 OFFSET $7
"""

STATS_SQL = """
SELECT
    (SELECT count(*) FROM projects WHERE tier IN ('verified', 'likely')) AS projects,
    (SELECT count(*) FROM projects WHERE tier = 'verified') AS verified_projects,
    (SELECT count(*) FROM projects WHERE tier = 'likely') AS likely_projects,
    (SELECT count(*) FROM projects WHERE tier = 'possible') AS possible_projects,
    (SELECT count(*) FROM projects WHERE tier = 'unattributed') AS unattributed_accounts,
    (SELECT count(*) FROM contracts WHERE deployed_at BETWEEN $1 AND $2) AS contracts,
    (SELECT count(*) FROM (
        SELECT deployer FROM contracts WHERE deployed_at BETWEEN $1 AND $2
        UNION SELECT uploader FROM wasm_uploads WHERE uploaded_at BETWEEN $1 AND $2) builders)
        AS builders,
    (SELECT count(DISTINCT c.login) FROM repo_contributors c
     JOIN projects p ON p.full_name = c.full_name
     WHERE p.tier IN ('verified', 'likely')) AS contributors,
    (SELECT count(DISTINCT country) FROM (
        SELECT r.country FROM projects p JOIN repos r ON r.full_name = p.full_name
        WHERE p.tier IN ('verified', 'likely')
        UNION SELECT u.country FROM projects p
            JOIN repo_contributors c ON c.full_name = p.full_name
            JOIN github_users u ON u.login = c.login
        WHERE p.tier IN ('verified', 'likely')) found
     WHERE country IS NOT NULL) AS countries,
    (SELECT count(*) FROM wasm_uploads WHERE uploaded_at BETWEEN $1 AND $2) AS wasm_uploads,
    (SELECT count(*) FROM failed_txs WHERE created_at BETWEEN $1 AND $2) AS failed_txs
"""

LINKS_SQL = f"""
SELECT l.subject_kind, l.subject, l.method, r.path
FROM links l
LEFT JOIN repo_refs r
       ON r.full_name = l.full_name AND r.kind = l.subject_kind AND r.value = l.subject
WHERE l.full_name = $1
ORDER BY {METHOD_RANK_SQL}, l.subject_kind, l.subject
"""

CONTRIBUTORS_SQL = """
SELECT c.login, c.url, c.avatar_url, c.contributions, u.country
FROM repo_contributors c
LEFT JOIN github_users u ON u.login = c.login
WHERE c.full_name = $1
ORDER BY c.contributions DESC, c.login
"""

TIMELINE_SQL = """
SELECT g.hour, count(c.contract_id) AS contracts
FROM generate_series($1::timestamptz, $2::timestamptz - interval '1 hour', interval '1 hour')
     AS g(hour)
LEFT JOIN contracts c ON c.deployed_at >= g.hour AND c.deployed_at < g.hour + interval '1 hour'
GROUP BY g.hour
ORDER BY g.hour
"""

INTEGRATIONS_SQL = """
SELECT i.partner AS slug, count(DISTINCT i.full_name) AS projects
FROM repo_integrations i
JOIN projects p ON p.full_name = i.full_name AND p.tier IN ('verified', 'likely')
GROUP BY i.partner
"""

INTEGRATION_USES_SQL = """
SELECT partner AS slug, method, evidence, path
FROM repo_integrations
WHERE full_name = $1
ORDER BY partner, method, evidence
"""

COUNTRIES_SQL = """
SELECT u.country, count(DISTINCT c.login) AS contributors
FROM repo_contributors c
JOIN projects p ON p.full_name = c.full_name AND p.tier IN ('verified', 'likely')
JOIN github_users u ON u.login = c.login
WHERE u.country IS NOT NULL
GROUP BY u.country
ORDER BY contributors DESC, u.country
LIMIT $1
"""

RESOURCE_SQL = {
    "projects": PROJECTS_SQL,
    "contracts": CONTRACTS_SQL,
    "wasm": WASM_SQL,
    "failed": FAILED_SQL,
}

Resource = Literal["projects", "contracts", "wasm", "failed"]


def window() -> tuple[datetime, datetime]:
    window = get_hackathon().window
    return window.start, window.end


async def list_page(
    resource: Resource,
    *,
    q: str | None = None,
    account: str | None = None,
    project_id: str | None = None,
    tiers: list[str] | None = None,
    track: str | None = None,
    integrations: list[str] | None = None,
    winners: bool = False,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[dict[str, Any]], int]:
    awards = places()
    winner_ids = list(awards) if winners else None
    args = (
        (q, account, project_id, tiers, limit, offset, track, integrations, winner_ids)
        if resource == "projects"
        else (*window(), q, account, project_id, limit, offset)
    )
    async with pool().acquire() as connection:
        rows = await connection.fetch(RESOURCE_SQL[resource], *args)
    total = rows[0]["total"] if rows else 0
    items = [{k: v for k, v in dict(row).items() if k != "total"} for row in rows]
    if resource == "projects":
        items = [{**item, "award": awards.get(item["project_id"])} for item in items]
    return items, total


async def fetch_stats() -> dict[str, int]:
    start, end = window()
    async with pool().acquire() as connection:
        return dict(await connection.fetchrow(STATS_SQL, start, end))


async def fetch_links(full_name: str) -> list[dict[str, Any]]:
    async with pool().acquire() as connection:
        return [dict(row) for row in await connection.fetch(LINKS_SQL, full_name)]


async def fetch_contributors(full_name: str) -> list[dict[str, Any]]:
    async with pool().acquire() as connection:
        return [dict(row) for row in await connection.fetch(CONTRIBUTORS_SQL, full_name)]


async def fetch_timeline() -> list[dict[str, Any]]:
    start, end = window()
    async with pool().acquire() as connection:
        return [dict(row) for row in await connection.fetch(TIMELINE_SQL, start, end)]


async def fetch_integration_uses(full_name: str) -> list[dict[str, Any]]:
    async with pool().acquire() as connection:
        rows = await connection.fetch(INTEGRATION_USES_SQL, full_name)
    names = {partner.slug: partner.name for partner in get_catalog().partners}
    return [{**row, "name": names[row["slug"]]} for row in map(dict, rows) if row["slug"] in names]


async def fetch_integrations() -> list[dict[str, Any]]:
    async with pool().acquire() as connection:
        counts = {row["slug"]: row["projects"] for row in await connection.fetch(INTEGRATIONS_SQL)}
    return [
        {
            **partner.model_dump(include={"slug", "name", "category", "site"}),
            "projects": counts.get(partner.slug, 0),
        }
        for partner in get_catalog().partners
    ]


async def fetch_countries(limit: int = 12) -> list[dict[str, Any]]:
    async with pool().acquire() as connection:
        return [dict(row) for row in await connection.fetch(COUNTRIES_SQL, limit)]

TOOLING_SQL = """
SELECT p.project_id, p.full_name, r.dependencies, COALESCE(r.tooling, '{}'::jsonb) AS tooling,
       ARRAY(SELECT i.partner FROM repo_integrations i
             WHERE i.full_name = p.full_name) AS integrations
FROM projects p
JOIN repos r ON r.full_name = p.full_name
WHERE p.tier IN ('verified', 'likely')
  AND ($1::text[] IS NULL OR NOT (p.project_id = ANY($1) OR p.full_name = ANY($1)))
"""


async def fetch_tooling() -> dict[str, Any]:
    from hackproof.github.dependencies import parse_major_version

    hidden = hidden_ids() or None
    async with pool().acquire() as connection:
        rows = await connection.fetch(TOOLING_SQL, hidden)

    total = len(rows)

    oz_count = 0
    wallets_count = 0
    freighter_count = 0
    passkey_count = 0

    soroban_versions: Counter[str] = Counter()
    stellar_versions: Counter[str] = Counter()
    framework_counts: Counter[str] = Counter()
    ai_counts: Counter[str] = Counter()

    for row in rows:
        deps = row["dependencies"] or {}
        if isinstance(deps, str):
            import json
            deps = json.loads(deps)
        packages = deps.get("packages", {}) or {}
        tooling = row["tooling"] or {}
        if isinstance(tooling, str):
            import json
            tooling = json.loads(tooling)
        integrations = set(row["integrations"] or [])

        # 1. OpenZeppelin Stellar Contracts
        has_oz = (
            tooling.get("openzeppelin")
            or any(
                p in packages
                for p in (
                    "stellar-contracts",
                    "openzeppelin-stellar-contracts",
                    "openzeppelin_stellar_contracts",
                    "@openzeppelin/contracts",
                    "@openzeppelin/stellar-contracts",
                )
            )
            or "openzeppelin" in integrations
        )
        if has_oz:
            oz_count += 1

        # 2. Stellar Wallets Kit
        has_wallets = (
            "@creit.tech/stellar-wallets-kit" in packages
            or "stellar-wallets-kit" in packages
            or "stellar-wallets-kit" in integrations
        )
        if has_wallets:
            wallets_count += 1

        # 3. Freighter API
        has_freighter = (
            "@stellar/freighter-api" in packages
            or "freighter" in integrations
            or "freighter-api" in packages
        )
        if has_freighter:
            freighter_count += 1

        # 4. Passkey Kit
        has_passkey = (
            "passkey-kit" in packages
            or "@stellar/passkey-kit" in packages
            or "passkey" in integrations
        )
        if has_passkey:
            passkey_count += 1

        # 5. soroban-sdk major versions
        if "soroban-sdk" in packages:
            ver = parse_major_version(packages["soroban-sdk"])
            soroban_versions[ver] += 1

        # 6. stellar-sdk JS versions
        sdk_spec = packages.get("@stellar/stellar-sdk") or packages.get("stellar-sdk")
        if sdk_spec:
            ver = parse_major_version(sdk_spec)
            stellar_versions[ver] += 1

        # 7. Frameworks
        fw = tooling.get("framework")
        if not fw or fw == "Other":
            if "next" in packages:
                fw = "Next.js"
            elif "vite" in packages:
                fw = "Vite"
            else:
                fw = "Other"
        framework_counts[fw] += 1

        # 8. AI tooling
        for tool in tooling.get("ai", []):
            ai_counts[tool] += 1

    def make_items(counter: dict[str, int]) -> list[dict[str, Any]]:
        items = []
        for name, count in counter.items():
            pct = round((count / total * 100), 1) if total > 0 else 0.0
            items.append({"name": name, "count": count, "percentage": pct})
        return sorted(items, key=lambda x: x["count"], reverse=True)

    kits_items = make_items({
        "Stellar Wallets Kit": wallets_count,
        "Freighter API": freighter_count,
        "OpenZeppelin Contracts": oz_count,
        "Passkey Kit": passkey_count,
    })

    return {
        "total_projects": total,
        "categories": [
            {
                "category": "Ecosystem Kits & Wallets",
                "description": "Adoption of official and partner Stellar libraries and kits",
                "items": kits_items,
            },
            {
                "category": "Soroban SDK Major Versions",
                "description": "Declared soroban-sdk version in Cargo.toml contracts",
                "items": make_items(dict(soroban_versions)),
            },
            {
                "category": "Stellar SDK (JS) Versions",
                "description": "Declared @stellar/stellar-sdk version in web applications",
                "items": make_items(dict(stellar_versions)),
            },
            {
                "category": "Frontend Frameworks",
                "description": "Application architecture: Next.js vs Vite vs other",
                "items": make_items(dict(framework_counts)),
            },
            {
                "category": "AI Tooling & Rules",
                "description": "Agent instructions, prompts and rules present in repository trees",
                "items": make_items(dict(ai_counts)),
            },
        ],
    }
