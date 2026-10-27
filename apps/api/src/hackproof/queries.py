from datetime import datetime
from typing import Any, Literal

from hackproof.db import pool
from hackproof.hackathon import get_hackathon

PROJECTS_SQL = """
SELECT p.project_id, p.full_name, r.url, p.footprint, p.tier, p.contracts, p.classic_ops, p.assets,
       p.builders, p.wasm_uploads, p.failed_txs, p.first_activity, p.last_activity,
       r.description, r.stars, r.forks, r.language, r.license, r.owner, r.owner_avatar,
       r.country, r.dependencies,
       r.window_commits, r.total_commits, r.mentions_hackathon, r.stellar_added_in_window,
       r.created_at, r.topics, r.discovered_via,
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
ORDER BY p.linked DESC, p.contracts DESC, p.classic_ops DESC, r.stars DESC NULLS LAST,
         p.last_activity DESC
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
    (SELECT count(*) FROM projects WHERE tier IN ('verified', 'declared', 'likely')) AS projects,
    (SELECT count(*) FROM projects WHERE tier = 'verified') AS verified_projects,
    (SELECT count(*) FROM projects WHERE tier = 'declared') AS declared_projects,
    (SELECT count(*) FROM projects WHERE tier = 'likely') AS likely_projects,
    (SELECT count(*) FROM projects WHERE tier = 'possible') AS possible_projects,
    (SELECT count(*) FROM projects WHERE tier = 'unattributed') AS unattributed_accounts,
    (SELECT count(*) FROM contracts WHERE deployed_at BETWEEN $1 AND $2) AS contracts,
    (SELECT count(*) FROM (
        SELECT deployer FROM contracts WHERE deployed_at BETWEEN $1 AND $2
        UNION SELECT uploader FROM wasm_uploads WHERE uploaded_at BETWEEN $1 AND $2
        UNION SELECT subject FROM links WHERE subject_kind = 'account') builders) AS builders,
    (SELECT count(DISTINCT c.login) FROM repo_contributors c
     JOIN projects p ON p.full_name = c.full_name
     WHERE p.tier IN ('verified', 'declared', 'likely')) AS contributors,
    (SELECT count(DISTINCT country) FROM (
        SELECT r.country FROM projects p JOIN repos r ON r.full_name = p.full_name
        WHERE p.tier IN ('verified', 'declared', 'likely')
        UNION SELECT u.country FROM projects p
            JOIN repo_contributors c ON c.full_name = p.full_name
            JOIN github_users u ON u.login = c.login
        WHERE p.tier IN ('verified', 'declared', 'likely')) found
     WHERE country IS NOT NULL) AS countries,
    (SELECT count(*) FROM wasm_uploads WHERE uploaded_at BETWEEN $1 AND $2) AS wasm_uploads,
    (SELECT count(*) FROM failed_txs WHERE created_at BETWEEN $1 AND $2) AS failed_txs
"""

LINKS_SQL = """
SELECT subject_kind, subject, method, confidence FROM links
WHERE full_name = $1 ORDER BY confidence DESC, subject_kind, subject
"""

CONTRIBUTORS_SQL = """
SELECT c.login, c.url, c.avatar_url, c.contributions, u.country
FROM repo_contributors c
LEFT JOIN github_users u ON u.login = c.login
WHERE c.full_name = $1
ORDER BY c.contributions DESC, c.login
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
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[dict[str, Any]], int]:
    args = (
        (q, account, project_id, tiers, limit, offset)
        if resource == "projects"
        else (*window(), q, account, project_id, limit, offset)
    )
    async with pool().acquire() as connection:
        rows = await connection.fetch(RESOURCE_SQL[resource], *args)
    total = rows[0]["total"] if rows else 0
    return [{k: v for k, v in dict(row).items() if k != "total"} for row in rows], total


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
