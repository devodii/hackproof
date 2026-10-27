from datetime import datetime
from typing import Any, Literal

from hackproof.config import get_settings
from hackproof.db import pool

PROJECTS_SQL = """
WITH keyed AS (
    SELECT c.deployer, c.deployed_at, wr.full_name,
           COALESCE('repo:' || wr.full_name, 'acct:' || c.deployer) AS project_id
    FROM contracts c
    LEFT JOIN wasm_repos wr USING (wasm_hash)
    WHERE c.deployed_at BETWEEN $1 AND $2
), grouped AS (
    SELECT project_id, max(full_name) AS full_name, count(*) AS contracts,
           count(DISTINCT deployer) AS builders, array_agg(DISTINCT deployer) AS deployers,
           min(deployed_at) AS first_deployed_at, max(deployed_at) AS last_deployed_at
    FROM keyed
    GROUP BY project_id
)
SELECT g.project_id, g.full_name, g.contracts, g.builders,
       g.first_deployed_at, g.last_deployed_at,
       r.description, r.stars, r.owner, r.owner_avatar, r.country,
       (SELECT count(DISTINCT w.wasm_hash) FROM wasm_uploads w
        WHERE w.uploader = ANY(g.deployers) AND w.uploaded_at BETWEEN $1 AND $2) AS wasm_uploads,
       (SELECT count(*) FROM failed_txs f
        WHERE f.source_account = ANY(g.deployers) AND f.created_at BETWEEN $1 AND $2) AS failed_txs,
       count(*) OVER () AS total
FROM grouped g
LEFT JOIN repos r ON r.full_name = g.full_name
WHERE ($3::text IS NULL
       OR g.project_id ILIKE '%' || $3 || '%'
       OR r.description ILIKE '%' || $3 || '%')
  AND ($4::text IS NULL OR $4 = ANY(g.deployers))
  AND ($5::text IS NULL OR g.project_id = $5)
ORDER BY g.contracts DESC, g.last_deployed_at DESC
LIMIT $6 OFFSET $7
"""

CONTRACTS_SQL = """
SELECT c.contract_id, c.deployer, c.wasm_hash, c.tx_hash, c.ledger, c.deployed_at,
       COALESCE('repo:' || wr.full_name, 'acct:' || c.deployer) AS project_id,
       count(*) OVER () AS total
FROM contracts c
LEFT JOIN wasm_repos wr USING (wasm_hash)
WHERE c.deployed_at BETWEEN $1 AND $2
  AND ($3::text IS NULL
       OR c.contract_id ILIKE '%' || $3 || '%'
       OR c.deployer ILIKE '%' || $3 || '%'
       OR c.wasm_hash ILIKE '%' || $3 || '%')
  AND ($4::text IS NULL OR c.deployer = $4)
  AND ($5::text IS NULL OR COALESCE('repo:' || wr.full_name, 'acct:' || c.deployer) = $5)
ORDER BY c.deployed_at DESC
LIMIT $6 OFFSET $7
"""

WASM_SQL = """
SELECT w.wasm_hash, w.uploader, w.tx_hash, w.size, w.source_repo, w.uploaded_at,
       wr.full_name,
       (SELECT count(*) FROM contracts c WHERE c.wasm_hash = w.wasm_hash) AS contracts,
       count(*) OVER () AS total
FROM wasm_uploads w
LEFT JOIN wasm_repos wr USING (wasm_hash)
WHERE w.uploaded_at BETWEEN $1 AND $2
  AND ($3::text IS NULL
       OR w.wasm_hash ILIKE '%' || $3 || '%'
       OR w.uploader ILIKE '%' || $3 || '%'
       OR w.source_repo ILIKE '%' || $3 || '%')
  AND ($4::text IS NULL OR w.uploader = $4)
  AND ($5::text IS NULL OR 'repo:' || wr.full_name = $5 OR 'acct:' || w.uploader = $5)
ORDER BY w.uploaded_at DESC
LIMIT $6 OFFSET $7
"""

FAILED_SQL = """
SELECT f.tx_hash, f.source_account, f.kind, f.result_code, f.ledger, f.created_at,
       count(*) OVER () AS total
FROM failed_txs f
WHERE f.created_at BETWEEN $1 AND $2
  AND ($3::text IS NULL
       OR f.tx_hash ILIKE '%' || $3 || '%'
       OR f.source_account ILIKE '%' || $3 || '%'
       OR f.result_code ILIKE '%' || $3 || '%')
  AND ($4::text IS NULL OR f.source_account = $4)
  AND ($5::text IS NULL OR f.source_account IN (
        SELECT c.deployer FROM contracts c
        LEFT JOIN wasm_repos wr USING (wasm_hash)
        WHERE COALESCE('repo:' || wr.full_name, 'acct:' || c.deployer) = $5))
ORDER BY f.created_at DESC
LIMIT $6 OFFSET $7
"""

STATS_SQL = """
WITH keyed AS (
    SELECT c.deployer, wr.full_name,
           COALESCE('repo:' || wr.full_name, 'acct:' || c.deployer) AS project_id
    FROM contracts c
    LEFT JOIN wasm_repos wr USING (wasm_hash)
    WHERE c.deployed_at BETWEEN $1 AND $2
)
SELECT
    (SELECT count(DISTINCT project_id) FROM keyed) AS projects,
    (SELECT count(DISTINCT full_name) FROM keyed) AS linked_projects,
    (SELECT count(*) FROM keyed) AS contracts,
    (SELECT count(DISTINCT deployer) FROM keyed) AS builders,
    (SELECT count(DISTINCT r.country) FROM repos r
     WHERE r.full_name IN (SELECT full_name FROM keyed)) AS countries,
    (SELECT count(*) FROM wasm_uploads WHERE uploaded_at BETWEEN $1 AND $2) AS wasm_uploads,
    (SELECT count(*) FROM failed_txs WHERE created_at BETWEEN $1 AND $2) AS failed_txs
"""


def window() -> tuple[datetime, datetime]:
    settings = get_settings()
    return settings.hack_start, settings.hack_end


RESOURCE_SQL = {
    "projects": PROJECTS_SQL,
    "contracts": CONTRACTS_SQL,
    "wasm": WASM_SQL,
    "failed": FAILED_SQL,
}

Resource = Literal["projects", "contracts", "wasm", "failed"]


async def list_page(
    resource: Resource,
    *,
    q: str | None = None,
    account: str | None = None,
    project_id: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[dict[str, Any]], int]:
    start, end = window()
    async with pool().acquire() as connection:
        rows = await connection.fetch(
            RESOURCE_SQL[resource], start, end, q, account, project_id, limit, offset
        )
    total = rows[0]["total"] if rows else 0
    return [{k: v for k, v in dict(row).items() if k != "total"} for row in rows], total


async def fetch_stats() -> dict[str, int]:
    start, end = window()
    async with pool().acquire() as connection:
        return dict(await connection.fetchrow(STATS_SQL, start, end))
