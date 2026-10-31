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
  AND ($10::text[] IS NULL OR NOT (
       p.project_id = ANY($10) OR p.full_name = ANY($10) OR r.owner = ANY($10)))
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
  AND ($8::text[] IS NULL OR NOT (
       COALESCE('repo:' || a.full_name, 'acct:' || c.deployer) = ANY($8)
       OR a.full_name = ANY($8)
       OR 'acct:' || c.deployer = ANY($8)
       OR c.deployer = ANY($8)
  ))
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
  AND ($8::text[] IS NULL OR NOT (
       COALESCE('repo:' || COALESCE(aa.full_name, aw.full_name), 'acct:' || w.uploader) = ANY($8)
       OR COALESCE(aa.full_name, aw.full_name) = ANY($8)
       OR 'acct:' || w.uploader = ANY($8)
       OR w.uploader = ANY($8)
  ))
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
  AND ($8::text[] IS NULL OR NOT (
       COALESCE(ap.project_id, 'acct:' || f.source_account) = ANY($8)
       OR 'acct:' || f.source_account = ANY($8)
       OR f.source_account = ANY($8)
  ))
ORDER BY f.created_at DESC
LIMIT $6 OFFSET $7
"""

STATS_SQL = """
SELECT
    (SELECT count(*) FROM projects WHERE tier IN ('verified', 'likely')
     AND ($3::text[] IS NULL OR NOT (project_id = ANY($3) OR full_name = ANY($3))))
     AS projects,
    (SELECT count(*) FROM projects WHERE tier = 'verified'
     AND ($3::text[] IS NULL OR NOT (project_id = ANY($3) OR full_name = ANY($3))))
     AS verified_projects,
    (SELECT count(*) FROM projects WHERE tier = 'likely'
     AND ($3::text[] IS NULL OR NOT (project_id = ANY($3) OR full_name = ANY($3))))
     AS likely_projects,
    (SELECT count(*) FROM projects WHERE tier = 'possible'
     AND ($3::text[] IS NULL OR NOT (project_id = ANY($3) OR full_name = ANY($3))))
     AS possible_projects,
    (SELECT count(*) FROM projects WHERE tier = 'unattributed'
     AND ($3::text[] IS NULL OR NOT (project_id = ANY($3) OR full_name = ANY($3))))
     AS unattributed_accounts,
    (SELECT count(*) FROM contracts c WHERE deployed_at BETWEEN $1 AND $2
     AND ($3::text[] IS NULL OR NOT (
          'acct:' || c.deployer = ANY($3)
          OR c.deployer = ANY($3)
          OR c.contract_id IN (
              SELECT subject FROM attribution
              WHERE subject_kind = 'contract'
                AND ('repo:' || full_name = ANY($3) OR full_name = ANY($3))
          )
     ))) AS contracts,
    (SELECT count(*) FROM (
        SELECT deployer FROM contracts WHERE deployed_at BETWEEN $1 AND $2
        UNION SELECT uploader FROM wasm_uploads WHERE uploaded_at BETWEEN $1 AND $2) builders
     WHERE $3::text[] IS NULL OR NOT ('acct:' || deployer = ANY($3) OR deployer = ANY($3)))
     AS builders,
    (SELECT count(DISTINCT c.login) FROM repo_contributors c
     JOIN projects p ON p.full_name = c.full_name
     WHERE p.tier IN ('verified', 'likely')
     AND ($3::text[] IS NULL OR NOT (p.project_id = ANY($3) OR p.full_name = ANY($3))))
     AS contributors,
    (SELECT count(DISTINCT country) FROM (
        SELECT r.country FROM projects p JOIN repos r ON r.full_name = p.full_name
        WHERE p.tier IN ('verified', 'likely')
          AND ($3::text[] IS NULL OR NOT (p.project_id = ANY($3) OR p.full_name = ANY($3)))
        UNION SELECT u.country FROM projects p
            JOIN repo_contributors c ON c.full_name = p.full_name
            JOIN github_users u ON u.login = c.login
        WHERE p.tier IN ('verified', 'likely')
          AND ($3::text[] IS NULL OR NOT (p.project_id = ANY($3) OR p.full_name = ANY($3)))) found
     WHERE country IS NOT NULL) AS countries,
    (SELECT count(*) FROM wasm_uploads WHERE uploaded_at BETWEEN $1 AND $2
     AND ($3::text[] IS NULL OR NOT ('acct:' || uploader = ANY($3) OR uploader = ANY($3))))
     AS wasm_uploads,
    (SELECT count(*) FROM failed_txs WHERE created_at BETWEEN $1 AND $2
     AND ($3::text[] IS NULL OR NOT (
          'acct:' || source_account = ANY($3) OR source_account = ANY($3))))
     AS failed_txs
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
WHERE ($1::text[] IS NULL OR NOT (p.project_id = ANY($1) OR p.full_name = ANY($1)))
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
  AND ($2::text[] IS NULL OR NOT (p.project_id = ANY($2) OR p.full_name = ANY($2)))
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


def is_hidden(target: str | None) -> bool:
    if not target:
        return False
    hidden = set(hidden_ids())
    return (
        target in hidden
        or f"repo:{target}" in hidden
        or f"acct:{target}" in hidden
        or target.removeprefix("repo:") in hidden
        or target.removeprefix("acct:") in hidden
    )


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
    if is_hidden(project_id) or is_hidden(account):
        return [], 0
    hidden = hidden_ids() or None
    awards = places()
    winner_ids = list(awards) if winners else None
    args = (
        (q, account, project_id, tiers, limit, offset, track, integrations, winner_ids, hidden)
        if resource == "projects"
        else (*window(), q, account, project_id, limit, offset, hidden)
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
    hidden = hidden_ids() or None
    async with pool().acquire() as connection:
        return dict(await connection.fetchrow(STATS_SQL, start, end, hidden))


async def fetch_links(full_name: str) -> list[dict[str, Any]]:
    if is_hidden(full_name):
        return []
    async with pool().acquire() as connection:
        return [dict(row) for row in await connection.fetch(LINKS_SQL, full_name)]


async def fetch_contributors(full_name: str) -> list[dict[str, Any]]:
    if is_hidden(full_name):
        return []
    async with pool().acquire() as connection:
        return [dict(row) for row in await connection.fetch(CONTRIBUTORS_SQL, full_name)]


async def fetch_timeline() -> list[dict[str, Any]]:
    start, end = window()
    async with pool().acquire() as connection:
        return [dict(row) for row in await connection.fetch(TIMELINE_SQL, start, end)]


async def fetch_integration_uses(full_name: str) -> list[dict[str, Any]]:
    if is_hidden(full_name):
        return []
    async with pool().acquire() as connection:
        rows = await connection.fetch(INTEGRATION_USES_SQL, full_name)
    names = {partner.slug: partner.name for partner in get_catalog().partners}
    return [{**row, "name": names[row["slug"]]} for row in map(dict, rows) if row["slug"] in names]


async def fetch_integrations() -> list[dict[str, Any]]:
    hidden = hidden_ids() or None
    async with pool().acquire() as connection:
        counts = {
            row["slug"]: row["projects"] for row in await connection.fetch(INTEGRATIONS_SQL, hidden)
        }
    return [
        {
            **partner.model_dump(include={"slug", "name", "category", "site"}),
            "projects": counts.get(partner.slug, 0),
        }
        for partner in get_catalog().partners
    ]


async def fetch_countries(limit: int = 12) -> list[dict[str, Any]]:
    hidden = hidden_ids() or None
    async with pool().acquire() as connection:
        return [dict(row) for row in await connection.fetch(COUNTRIES_SQL, limit, hidden)]
