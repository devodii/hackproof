from datetime import UTC, datetime
from typing import Any, Literal

from hackproof.db import pool
from hackproof.hackathon import hackathons
from hackproof.integrations.catalog import get_catalog
from hackproof.scope import current, selected_slug
from hackproof.sql_loader import load_sql

TOP_BUILDERS = 12
MAX_BUILDERS = 1_000

RESOURCE_SQL = {
    "projects": "queries/projects",
    "contracts": "queries/contracts",
    "wasm": "queries/wasm",
    "failed": "queries/failed",
}

Resource = Literal["projects", "contracts", "wasm", "failed"]


def window() -> tuple[datetime, datetime]:
    window = current().window
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
    everywhere: bool = False,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[dict[str, Any]], int]:
    hackathon = current()
    placed = hackathon.places()
    awards_of = {slug: item.places() for slug, item in hackathons().items()}
    wanted = project_ids
    if wanted is None and (winners or awards):
        wanted = [
            pid for pid, place in placed.items() if awards is None or place in awards
        ]
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
            None if everywhere else hackathon.slug,
        )
        if resource == "projects"
        else (*window(), q, account, project_id, limit, offset)
    )
    async with pool().acquire() as connection:
        rows = await connection.fetch(load_sql(RESOURCE_SQL[resource]), *args)
    total = rows[0]["total"] if rows else 0
    items = [{k: v for k, v in dict(row).items() if k != "total"} for row in rows]
    if resource == "projects":
        items = [
            {
                **item,
                "award": awards_of.get(item["hackathon"], {}).get(item["project_id"]),
            }
            for item in items
        ]
    return items, total


async def fetch_hackathons() -> list[dict[str, Any]]:
    async with pool().acquire() as connection:
        counts = {
            row["hackathon"]: dict(row)
            for row in await connection.fetch(load_sql("queries/hackathons"))
        }
    now = datetime.now(UTC)
    return [
        {
            "slug": hackathon.slug,
            "name": hackathon.name,
            "summary": hackathon.summary,
            "website": hackathon.website,
            "location": hackathon.location,
            "starts_at": hackathon.window.start,
            "ends_at": hackathon.window.end,
            "status": "upcoming"
            if now < hackathon.window.start
            else "live"
            if now <= hackathon.window.end
            else "past",
            "indexed": hackathon.slug in counts,
            "projects": counts.get(hackathon.slug, {}).get("projects", 0),
            "verified_projects": counts.get(hackathon.slug, {}).get(
                "verified_projects", 0
            ),
            "contracts": counts.get(hackathon.slug, {}).get("contracts", 0),
            "winners": len(hackathon.awards),
        }
        for hackathon in hackathons().values()
    ]


async def fetch_stats() -> dict[str, int]:
    start, end = window()
    async with pool().acquire() as connection:
        return dict(
            await connection.fetchrow(
                load_sql("queries/stats"), start, end, current().slug
            )
        )


async def fetch_links(full_name: str) -> list[dict[str, Any]]:
    async with pool().acquire() as connection:
        return [
            dict(row)
            for row in await connection.fetch(load_sql("queries/links"), full_name)
        ]


async def fetch_contributors(full_name: str) -> list[dict[str, Any]]:
    async with pool().acquire() as connection:
        return [
            dict(row)
            for row in await connection.fetch(
                load_sql("queries/contributors"), full_name
            )
        ]


async def fetch_timeline() -> list[dict[str, Any]]:
    start, end = window()
    async with pool().acquire() as connection:
        return [
            dict(row)
            for row in await connection.fetch(load_sql("queries/timeline"), start, end)
        ]


async def fetch_integration_uses(full_name: str) -> list[dict[str, Any]]:
    async with pool().acquire() as connection:
        rows = await connection.fetch(load_sql("queries/integration_uses"), full_name)
    names = {partner.slug: partner.name for partner in get_catalog().partners}
    return [
        {**row, "name": names[row["slug"]]}
        for row in map(dict, rows)
        if row["slug"] in names
    ]


async def fetch_tool_uses(full_name: str) -> list[dict[str, Any]]:
    async with pool().acquire() as connection:
        rows = await connection.fetch(load_sql("queries/tool_uses"), full_name)
    names = {tool.slug: tool.name for tool in get_catalog().tools}
    return [
        {**row, "name": names[row["slug"]]}
        for row in map(dict, rows)
        if row["slug"] in names
    ]


async def fetch_tools() -> list[dict[str, Any]]:
    async with pool().acquire() as connection:
        counts = {
            row["slug"]: row["projects"]
            for row in await connection.fetch(
                load_sql("queries/tools"), selected_slug()
            )
        }
    return [
        {
            **tool.model_dump(include={"slug", "name", "site"}),
            "projects": counts.get(tool.slug, 0),
            "deep": tool.profile is not None,
        }
        for tool in get_catalog().tools
    ]


async def fetch_integrations() -> list[dict[str, Any]]:
    async with pool().acquire() as connection:
        counts = {
            row["slug"]: row["projects"]
            for row in await connection.fetch(
                load_sql("queries/integrations"), selected_slug()
            )
        }
    return [
        {
            **partner.model_dump(include={"slug", "name", "category", "site"}),
            "projects": counts.get(partner.slug, 0),
            "deep": partner.profile is not None,
        }
        for partner in get_catalog().partners
    ]


async def fetch_countries(limit: int = 12) -> list[dict[str, Any]]:
    async with pool().acquire() as connection:
        return [
            dict(row)
            for row in await connection.fetch(
                load_sql("queries/countries"), limit, current().slug
            )
        ]


async def fetch_wrapped() -> dict[str, Any]:
    start, end = window()
    slug = current().slug
    agents = [
        login.lower() for agent in get_catalog().agents for login in agent.authors
    ]
    async with pool().acquire() as connection:
        totals = dict(
            await connection.fetchrow(
                load_sql("wrapped/totals"), agents, start, end, slug
            )
        )
        operations = await connection.fetch(load_sql("wrapped/operations"), start, end)
        teams = await connection.fetch(load_sql("wrapped/teams"), agents, slug)
        multi_team = await connection.fetch(
            load_sql("wrapped/builders"), agents, 2, MAX_BUILDERS, slug
        )
        top = await connection.fetch(
            load_sql("wrapped/builders"), agents, 1, TOP_BUILDERS, slug
        )
    return {
        **totals,
        "operations_by_type": [dict(row) for row in operations],
        "team_sizes": [dict(row) for row in teams],
        "multi_team_builders": [dict(row) for row in multi_team],
        "top_builders": [
            dict(row) for row in sorted(top, key=lambda row: -row["contributions"])
        ],
    }


async def fetch_agents() -> list[dict[str, Any]]:
    async with pool().acquire() as connection:
        counts = {
            row["slug"]: row["projects"]
            for row in await connection.fetch(
                load_sql("queries/agents"), selected_slug()
            )
        }
    return [
        {
            **agent.model_dump(include={"slug", "name", "site"}),
            "projects": counts.get(agent.slug, 0),
        }
        for agent in get_catalog().agents
    ]


async def fetch_person(login: str) -> dict[str, Any] | None:
    async with pool().acquire() as connection:
        rows = [
            dict(row)
            for row in await connection.fetch(load_sql("queries/person"), login)
        ]
    if not rows:
        return None
    commits = {f"repo:{row['full_name']}": row["contributions"] for row in rows}
    projects, _ = await list_page(
        "projects",
        tiers=["verified", "likely"],
        project_ids=list(commits),
        everywhere=True,
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
