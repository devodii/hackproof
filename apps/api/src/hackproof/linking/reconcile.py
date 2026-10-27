import logging

import asyncpg
from pydantic import BaseModel

from hackproof.config import get_settings
from hackproof.db import open_pool, pool
from hackproof.hackathon import get_hackathon
from hackproof.linking.methods import CONFIDENCE, LinkMethod
from hackproof.linking.repo_ref import normalize_repo

log = logging.getLogger("hackproof.reconcile")

MAX_REPOS_PER_ACCOUNT = 8
MIN_WINDOW_COMMITS = 3

HACKERS = """
SELECT account FROM accounts WHERE funder = $3 AND funded_at BETWEEN $1 AND $2
UNION SELECT deployer FROM contracts
UNION SELECT uploader FROM wasm_uploads
"""

EVIDENCE = {
    LinkMethod.CONTRACT_IN_REPO: """
        SELECT r.full_name, 'contract', r.value FROM repo_refs r
        WHERE r.kind = 'contract' AND r.value IN (SELECT contract_id FROM contracts)
    """,
    LinkMethod.WASM_HASH_MATCH: """
        SELECT r.full_name, 'wasm', r.value FROM repo_refs r
        WHERE r.kind = 'wasm' AND (r.value IN (SELECT wasm_hash FROM wasm_uploads)
                                   OR r.value IN (SELECT wasm_hash FROM contracts))
    """,
    LinkMethod.DEPLOYER_IN_REPO: f"""
        SELECT r.full_name, 'account', r.value FROM repo_refs r
        WHERE r.kind = 'account'
          AND r.value IN ({HACKERS})
          AND r.value <> ALL($4::text[])
          AND r.value NOT IN (
              SELECT value FROM repo_refs WHERE kind = 'account'
              GROUP BY value HAVING count(*) > $5)
    """,
    LinkMethod.ASSET_IN_REPO: f"""
        SELECT r.full_name, 'asset', r.value FROM repo_refs r
        WHERE r.kind = 'asset'
          AND split_part(r.value, ':', 2) IN ({HACKERS})
          AND r.value IN (SELECT asset FROM classic_ops WHERE asset IS NOT NULL
                          AND occurred_at BETWEEN $1 AND $2)
    """,
}

SINGLE_OWNER_WASM = """
    SELECT wasm_hash FROM wasm_uploads GROUP BY wasm_hash HAVING count(DISTINCT uploader) = 1
"""

FOOTPRINT = [
    """
    SELECT l.full_name, 'account', c.deployer FROM links l
    JOIN contracts c ON l.subject_kind = 'contract' AND c.contract_id = l.subject
    """,
    f"""
    SELECT l.full_name, 'account', w.uploader FROM links l
    JOIN wasm_uploads w ON l.subject_kind = 'wasm' AND w.wasm_hash = l.subject
    WHERE l.subject IN ({SINGLE_OWNER_WASM})
    """,
    """
    SELECT l.full_name, 'contract', c.contract_id FROM links l
    JOIN contracts c ON l.subject_kind = 'account' AND c.deployer = l.subject
    """,
    """
    SELECT l.full_name, 'asset', a.asset FROM links l
    JOIN (SELECT DISTINCT asset FROM classic_ops WHERE asset IS NOT NULL) a
      ON l.subject_kind = 'account' AND split_part(a.asset, ':', 2) = l.subject
    """,
]

REPO_PROJECTS = """
INSERT INTO projects
WITH contract_stats AS (
    SELECT a.full_name, count(*) AS contracts, count(DISTINCT c.deployer) AS builders,
           min(c.deployed_at) AS first_at, max(c.deployed_at) AS last_at
    FROM contracts c
    JOIN attribution a ON a.subject_kind = 'contract' AND a.subject = c.contract_id
    WHERE c.deployed_at BETWEEN $1 AND $2
    GROUP BY a.full_name
), op_stats AS (
    SELECT a.full_name, count(*) AS classic_ops FROM classic_ops o
    JOIN attribution a ON a.subject_kind = 'account' AND a.subject = o.source_account
    WHERE o.occurred_at BETWEEN $1 AND $2
    GROUP BY a.full_name
), asset_stats AS (
    SELECT full_name, count(*) AS assets FROM attribution
    WHERE subject_kind = 'asset' GROUP BY full_name
), wasm_stats AS (
    SELECT COALESCE(aa.full_name, aw.full_name) AS full_name, count(DISTINCT w.wasm_hash) AS wasm
    FROM wasm_uploads w
    LEFT JOIN attribution aa ON aa.subject_kind = 'account' AND aa.subject = w.uploader
    LEFT JOIN attribution aw ON aw.subject_kind = 'wasm' AND aw.subject = w.wasm_hash
    WHERE w.uploaded_at BETWEEN $1 AND $2
    GROUP BY 1
), failed_stats AS (
    SELECT a.full_name, count(*) AS failed FROM failed_txs f
    JOIN attribution a ON a.subject_kind = 'account' AND a.subject = f.source_account
    WHERE f.created_at BETWEEN $1 AND $2
    GROUP BY a.full_name
)
SELECT 'repo:' || r.full_name, r.full_name,
       CASE WHEN COALESCE(cs.contracts, 0) > 0 THEN 'contracts'
            WHEN COALESCE(os.classic_ops, 0) + COALESCE(ast.assets, 0) > 0 THEN 'classic'
            ELSE 'github' END,
       CASE
           WHEN EXISTS (SELECT 1 FROM links l WHERE l.full_name = r.full_name)
                AND COALESCE(cs.contracts, 0) + COALESCE(os.classic_ops, 0)
                    + COALESCE(ast.assets, 0) + COALESCE(ws.wasm, 0) + COALESCE(fs.failed, 0) > 0
                THEN 'verified'
           WHEN EXISTS (SELECT 1 FROM unnest(r.discovered_via) via WHERE via LIKE 'seed:%')
                OR (r.mentions_hackathon AND COALESCE(r.window_commits, 0) > 0) THEN 'declared'
           WHEN jsonb_array_length(r.dependencies -> 'ecosystems') > 0
                AND COALESCE(r.window_commits, 0) > 0
                AND (r.created_at BETWEEN $1 AND $2
                     OR COALESCE(r.stellar_added_in_window, FALSE)) THEN 'likely'
           ELSE 'possible' END,
       COALESCE(cs.contracts, 0), COALESCE(os.classic_ops, 0), COALESCE(ast.assets, 0),
       COALESCE(ws.wasm, 0), COALESCE(fs.failed, 0), COALESCE(cs.builders, 0),
       COALESCE(cs.first_at, r.pushed_at), COALESCE(cs.last_at, r.pushed_at),
       EXISTS (SELECT 1 FROM links l WHERE l.full_name = r.full_name)
FROM repos r
LEFT JOIN contract_stats cs USING (full_name)
LEFT JOIN op_stats os USING (full_name)
LEFT JOIN asset_stats ast USING (full_name)
LEFT JOIN wasm_stats ws USING (full_name)
LEFT JOIN failed_stats fs USING (full_name)
WHERE r.full_name IN (SELECT full_name FROM links)
   OR EXISTS (
       SELECT 1 FROM unnest(r.discovered_via) via WHERE via LIKE 'seed:%' OR via = 'wasm_meta')
   OR (r.mentions_hackathon AND COALESCE(r.window_commits, 0) > 0)
   OR (jsonb_array_length(r.dependencies -> 'ecosystems') > 0
       AND (r.mentions_hackathon OR COALESCE(r.window_commits, 0) >= $3
            OR COALESCE(r.stellar_added_in_window, FALSE)
            OR r.created_at BETWEEN $1 AND $2))
"""

ACCOUNT_PROJECTS = f"""
INSERT INTO projects
WITH builders AS (
    SELECT deployer AS account FROM contracts WHERE deployed_at BETWEEN $1 AND $2
    UNION SELECT uploader FROM wasm_uploads WHERE uploaded_at BETWEEN $1 AND $2
    UNION SELECT split_part(asset, ':', 2) FROM classic_ops
          WHERE asset IS NOT NULL AND occurred_at BETWEEN $1 AND $2
            AND split_part(asset, ':', 2) IN ({HACKERS})
), orphans AS (
    SELECT account FROM builders
    WHERE account NOT IN (SELECT subject FROM links WHERE subject_kind = 'account')
)
SELECT 'acct:' || o.account, NULL,
       CASE WHEN EXISTS (SELECT 1 FROM contracts c WHERE c.deployer = o.account
                         AND c.deployed_at BETWEEN $1 AND $2) THEN 'contracts' ELSE 'classic' END,
       'unattributed',
       (SELECT count(*) FROM contracts c
        WHERE c.deployer = o.account AND c.deployed_at BETWEEN $1 AND $2),
       (SELECT count(*) FROM classic_ops x
        WHERE x.source_account = o.account AND x.occurred_at BETWEEN $1 AND $2),
       (SELECT count(DISTINCT asset) FROM classic_ops x
        WHERE split_part(x.asset, ':', 2) = o.account AND x.occurred_at BETWEEN $1 AND $2),
       (SELECT count(DISTINCT wasm_hash) FROM wasm_uploads w
        WHERE w.uploader = o.account AND w.uploaded_at BETWEEN $1 AND $2),
       (SELECT count(*) FROM failed_txs f
        WHERE f.source_account = o.account AND f.created_at BETWEEN $1 AND $2),
       1,
       (SELECT min(at) FROM (
            SELECT deployed_at AS at FROM contracts WHERE deployer = o.account
            UNION ALL SELECT uploaded_at FROM wasm_uploads WHERE uploader = o.account
            UNION ALL SELECT occurred_at FROM classic_ops WHERE source_account = o.account) a),
       (SELECT max(at) FROM (
            SELECT deployed_at AS at FROM contracts WHERE deployer = o.account
            UNION ALL SELECT uploaded_at FROM wasm_uploads WHERE uploader = o.account
            UNION ALL SELECT occurred_at FROM classic_ops WHERE source_account = o.account) a),
       FALSE
FROM orphans o
"""


class Report(BaseModel):
    links_by_method: dict[str, int]
    projects_by_footprint: dict[str, int]
    projects_by_tier: dict[str, int]
    linked_projects: int


async def _insert_links(
    connection: asyncpg.Connection, method: LinkMethod, select: str, *params: object
) -> None:
    await connection.execute(
        f"""
        INSERT INTO links (full_name, subject_kind, subject, method, confidence)
        SELECT s.full_name, s.subject_kind, s.subject, '{method}', {CONFIDENCE[method]}
        FROM ({select}) AS s(full_name, subject_kind, subject)
        ON CONFLICT DO NOTHING
        """,
        *params,
    )


async def _wasm_meta_links(connection: asyncpg.Connection) -> None:
    canonical = {
        row["full_name"].lower(): row["full_name"]
        for row in await connection.fetch("SELECT full_name FROM repos")
    }
    rows = await connection.fetch(
        "SELECT DISTINCT wasm_hash, source_repo FROM wasm_uploads WHERE source_repo IS NOT NULL"
    )
    links = []
    for row in rows:
        name = normalize_repo(row["source_repo"])
        if name and name.lower() in canonical:
            links.append(
                (
                    canonical[name.lower()],
                    "wasm",
                    row["wasm_hash"],
                    LinkMethod.WASM_META,
                    CONFIDENCE[LinkMethod.WASM_META],
                )
            )
    await connection.executemany(
        "INSERT INTO links VALUES ($1, $2, $3, $4, $5) ON CONFLICT DO NOTHING", links
    )


async def reconcile(connection: asyncpg.Connection) -> Report:
    settings, hackathon = get_settings(), get_hackathon()
    window = hackathon.window
    infra = [settings.friendbot_account, *hackathon.discovery.known_infra_accounts]
    pull = (window.pull_start, window.end)
    evidence_params: dict[LinkMethod, tuple[object, ...]] = {
        LinkMethod.CONTRACT_IN_REPO: (),
        LinkMethod.WASM_HASH_MATCH: (),
        LinkMethod.DEPLOYER_IN_REPO: (
            *pull,
            settings.friendbot_account,
            infra,
            MAX_REPOS_PER_ACCOUNT,
        ),
        LinkMethod.ASSET_IN_REPO: (*pull, settings.friendbot_account),
    }

    async with connection.transaction():
        await connection.execute("DELETE FROM links")
        await connection.execute("DELETE FROM projects")
        await _wasm_meta_links(connection)
        for method, select in EVIDENCE.items():
            await _insert_links(connection, method, select, *evidence_params[method])
        for select in FOOTPRINT:
            await _insert_links(connection, LinkMethod.FOOTPRINT, select)
        official = (window.start, window.end)
        await connection.execute(REPO_PROJECTS, *official, MIN_WINDOW_COMMITS)
        await connection.execute(ACCOUNT_PROJECTS, *official, settings.friendbot_account)

    methods = await connection.fetch("SELECT method, count(*) AS n FROM links GROUP BY method")
    footprints = await connection.fetch(
        "SELECT footprint, count(*) AS n FROM projects GROUP BY footprint"
    )
    tiers = await connection.fetch("SELECT tier, count(*) AS n FROM projects GROUP BY tier")
    linked = await connection.fetchval("SELECT count(DISTINCT full_name) FROM links")
    return Report(
        links_by_method={row["method"]: row["n"] for row in methods},
        projects_by_footprint={row["footprint"]: row["n"] for row in footprints},
        projects_by_tier={row["tier"]: row["n"] for row in tiers},
        linked_projects=linked,
    )


async def run_reconcile() -> None:
    await open_pool()
    async with pool().acquire() as connection:
        report = await reconcile(connection)
    log.info("%s", report.model_dump_json(indent=2))
