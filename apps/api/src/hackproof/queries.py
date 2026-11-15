from datetime import datetime
from typing import Any, Literal

from hackproof.db import pool
from hackproof.hackathon import get_hackathon, places
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
       ARRAY(SELECT t.tool FROM repo_tools t WHERE t.full_name = p.full_name
             GROUP BY t.tool ORDER BY t.tool) AS tools,
       ARRAY(SELECT a.agent FROM repo_agents a WHERE a.full_name = p.full_name
             GROUP BY a.agent ORDER BY a.agent) AS agents,
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
  AND ($10::text[] IS NULL OR EXISTS (
       SELECT 1 FROM repo_tools t
       WHERE t.full_name = p.full_name AND t.tool = ANY($10)))
  AND ($11::text[] IS NULL OR EXISTS (
       SELECT 1 FROM repo_agents a
       WHERE a.full_name = p.full_name AND a.agent = ANY($11)))
  AND ($12::text[] IS NULL OR r.language = ANY($12))
  AND ($13::text[] IS NULL OR r.country = ANY($13))
  AND ($14::text[] IS NULL
       OR ('contracts' = ANY($14) AND p.contracts > 0)
       OR ('failed' = ANY($14) AND p.failed_txs > 0))
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

PERSON_SQL = """
SELECT c.login, c.url, c.avatar_url, c.contributions, c.full_name, u.country
FROM repo_contributors c
LEFT JOIN github_users u ON u.login = c.login
WHERE lower(c.login) = lower($1)
ORDER BY c.contributions DESC, c.full_name
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

TOOLS_SQL = """
SELECT t.tool AS slug, count(DISTINCT t.full_name) AS projects
FROM repo_tools t
JOIN projects p ON p.full_name = t.full_name AND p.tier IN ('verified', 'likely')
GROUP BY t.tool
"""

AGENTS_SQL = """
SELECT a.agent AS slug, count(DISTINCT a.full_name) AS projects
FROM repo_agents a
JOIN projects p ON p.full_name = a.full_name AND p.tier IN ('verified', 'likely')
GROUP BY a.agent
"""

TOOL_USES_SQL = """
SELECT tool AS slug, method, evidence, path
FROM repo_tools
WHERE full_name = $1
ORDER BY tool, method, evidence
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

SHIPPED = "p.tier IN ('verified', 'likely')"
HUMAN = "lower(c.login) <> ALL($1::text[]) AND c.login NOT LIKE '%[bot]'"
TOP_BUILDERS = 12
MAX_BUILDERS = 1_000

WRAPPED_TOTALS_SQL = f"""
SELECT
    (SELECT count(DISTINCT c.login) FROM repo_contributors c
     JOIN projects p ON p.full_name = c.full_name
     WHERE {SHIPPED} AND {HUMAN}) AS builders,
    (SELECT count(*) FROM accounts WHERE funded_at BETWEEN $2 AND $3) AS accounts_funded,
    (SELECT count(DISTINCT deployer) FROM contracts
     WHERE deployed_at BETWEEN $2 AND $3) AS deployers,
    (SELECT count(*) FROM classic_ops WHERE occurred_at BETWEEN $2 AND $3) AS operations,
    (SELECT coalesce(max(n), 0) FROM (
        SELECT count(*) AS n FROM contracts WHERE deployed_at BETWEEN $2 AND $3
        GROUP BY wasm_hash) shared) AS largest_wasm_contracts
"""

WRAPPED_OPERATIONS_SQL = """
SELECT op_type AS label, count(*) AS value
FROM classic_ops
WHERE occurred_at BETWEEN $1 AND $2
GROUP BY op_type
ORDER BY value DESC, op_type
LIMIT 5
"""

WRAPPED_TEAMS_SQL = f"""
SELECT least(n, 5)::text AS label, count(*) AS value
FROM (
    SELECT c.full_name, count(*) AS n
    FROM repo_contributors c JOIN projects p ON p.full_name = c.full_name
    WHERE {SHIPPED} AND {HUMAN}
    GROUP BY c.full_name) teams
GROUP BY 1
ORDER BY 1
"""

WRAPPED_BUILDERS_SQL = f"""
SELECT c.login, max(c.avatar_url) AS avatar_url,
       count(DISTINCT c.full_name) AS projects, sum(c.contributions)::int AS contributions
FROM repo_contributors c JOIN projects p ON p.full_name = c.full_name
WHERE {SHIPPED} AND {HUMAN}
GROUP BY c.login
HAVING count(DISTINCT c.full_name) >= $2
ORDER BY projects DESC, contributions DESC, c.login
LIMIT $3
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
    tools: list[str] | None = None,
    agents: list[str] | None = None,
    languages: list[str] | None = None,
    countries: list[str] | None = None,
    activity: list[str] | None = None,
    awards: list[str] | None = None,
    project_ids: list[str] | None = None,
    winners: bool = False,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[dict[str, Any]], int]:
    placed = places()
    wanted = project_ids
    if wanted is None and (winners or awards):
        wanted = [pid for pid, place in placed.items() if awards is None or place in awards]
    args = (
        (
            q,
            account,
            project_id,
            tiers,
            limit,
            offset,
            track,
            integrations,
            wanted,
            tools,
            agents,
            languages,
            countries,
            activity,
        )
        if resource == "projects"
        else (*window(), q, account, project_id, limit, offset)
    )
    async with pool().acquire() as connection:
        rows = await connection.fetch(RESOURCE_SQL[resource], *args)
    total = rows[0]["total"] if rows else 0
    items = [{k: v for k, v in dict(row).items() if k != "total"} for row in rows]
    if resource == "projects":
        items = [{**item, "award": placed.get(item["project_id"])} for item in items]
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


async def fetch_tool_uses(full_name: str) -> list[dict[str, Any]]:
    async with pool().acquire() as connection:
        rows = await connection.fetch(TOOL_USES_SQL, full_name)
    names = {tool.slug: tool.name for tool in get_catalog().tools}
    return [{**row, "name": names[row["slug"]]} for row in map(dict, rows) if row["slug"] in names]


async def fetch_tools() -> list[dict[str, Any]]:
    async with pool().acquire() as connection:
        counts = {row["slug"]: row["projects"] for row in await connection.fetch(TOOLS_SQL)}
    return [
        {**tool.model_dump(include={"slug", "name", "site"}), "projects": counts.get(tool.slug, 0)}
        for tool in get_catalog().tools
    ]


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


async def fetch_wrapped() -> dict[str, Any]:
    start, end = window()
    agents = [login.lower() for agent in get_catalog().agents for login in agent.authors]
    async with pool().acquire() as connection:
        totals = dict(await connection.fetchrow(WRAPPED_TOTALS_SQL, agents, start, end))
        operations = await connection.fetch(WRAPPED_OPERATIONS_SQL, start, end)
        teams = await connection.fetch(WRAPPED_TEAMS_SQL, agents)
        multi_team = await connection.fetch(WRAPPED_BUILDERS_SQL, agents, 2, MAX_BUILDERS)
        top = await connection.fetch(WRAPPED_BUILDERS_SQL, agents, 1, TOP_BUILDERS)
    return {
        **totals,
        "operations_by_type": [dict(row) for row in operations],
        "team_sizes": [dict(row) for row in teams],
        "multi_team_builders": [dict(row) for row in multi_team],
        "top_builders": [dict(row) for row in sorted(top, key=lambda row: -row["contributions"])],
    }


async def fetch_agents() -> list[dict[str, Any]]:
    async with pool().acquire() as connection:
        counts = {row["slug"]: row["projects"] for row in await connection.fetch(AGENTS_SQL)}
    return [
        {
            **agent.model_dump(include={"slug", "name", "site"}),
            "projects": counts.get(agent.slug, 0),
        }
        for agent in get_catalog().agents
    ]


async def fetch_person(login: str) -> dict[str, Any] | None:
    async with pool().acquire() as connection:
        rows = [dict(row) for row in await connection.fetch(PERSON_SQL, login)]
    if not rows:
        return None
    commits = {f"repo:{row['full_name']}": row["contributions"] for row in rows}
    projects, _ = await list_page(
        "projects",
        tiers=["verified", "likely"],
        project_ids=list(commits),
        limit=len(commits),
    )
    if not projects:
        return None
    first = rows[0]
    return {
        "login": first["login"],
        "url": first["url"],
        "avatar_url": first["avatar_url"],
        "country": first["country"],
        "contributions": sum(commits[project["project_id"]] for project in projects),
        "projects": sorted(
            (
                {"project": project, "contributions": commits[project["project_id"]]}
                for project in projects
            ),
            key=lambda item: (-item["contributions"], item["project"]["project_id"]),
        ),
    }
