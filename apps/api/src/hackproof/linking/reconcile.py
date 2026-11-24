import logging

import asyncpg
from pydantic import BaseModel
from trawl.github.refs import normalize_repo

from hackproof.config import get_settings
from hackproof.db import open_pool, pool
from hackproof.hackathon import get_hackathon
from hackproof.linking.methods import LinkMethod
from hackproof.sql_loader import load_sql

log = logging.getLogger("hackproof.reconcile")

MAX_REPOS_PER_ACCOUNT = 8
MIN_WINDOW_COMMITS = 3
MIN_LIKELY_COMMITS = 5

EVIDENCE = {
    LinkMethod.CONTRACT_IN_REPO: "reconcile/link_contract_in_repo",
    LinkMethod.WASM_HASH_MATCH: "reconcile/link_wasm_hash_match",
    LinkMethod.DEPLOYER_IN_REPO: "reconcile/link_deployer_in_repo",
    LinkMethod.ASSET_IN_REPO: "reconcile/link_asset_in_repo",
}

FOOTPRINT = [
    "reconcile/link_footprint_deployers",
    "reconcile/link_footprint_uploaders",
    "reconcile/link_footprint_contracts",
    "reconcile/link_footprint_assets",
]


class Report(BaseModel):
    links_by_method: dict[str, int]
    projects_by_footprint: dict[str, int]
    projects_by_tier: dict[str, int]


async def _insert_links(
    connection: asyncpg.Connection, method: LinkMethod, query: str, *params: object
) -> None:
    await connection.execute(load_sql(query), method.value, *params)


async def _wasm_meta_links(connection: asyncpg.Connection, hackathon: str) -> None:
    canonical = {
        row["full_name"].lower(): row["full_name"]
        for row in await connection.fetch(load_sql("reconcile/repo_names"), hackathon)
    }
    rows = await connection.fetch(load_sql("reconcile/wasm_sources"))
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
                )
            )
    await connection.executemany(load_sql("reconcile/insert_link"), links)


async def reconcile(connection: asyncpg.Connection) -> Report:
    settings, hackathon = get_settings(), get_hackathon()
    window = hackathon.window
    infra = [settings.friendbot_account, *hackathon.indexing().known_infra_accounts]
    pull = (window.pull_start, window.end)
    evidence_params: dict[LinkMethod, tuple[object, ...]] = {
        LinkMethod.CONTRACT_IN_REPO: (hackathon.slug,),
        LinkMethod.WASM_HASH_MATCH: (hackathon.slug,),
        LinkMethod.DEPLOYER_IN_REPO: (
            *pull,
            settings.friendbot_account,
            infra,
            MAX_REPOS_PER_ACCOUNT,
            hackathon.slug,
        ),
        LinkMethod.ASSET_IN_REPO: (*pull, settings.friendbot_account, hackathon.slug),
    }

    async with connection.transaction():
        await connection.execute(load_sql("reconcile/reset_links"), hackathon.slug)
        await connection.execute(load_sql("reconcile/reset_projects"), hackathon.slug)
        await _wasm_meta_links(connection, hackathon.slug)
        for method, query in EVIDENCE.items():
            await _insert_links(connection, method, query, *evidence_params[method])
        for query in FOOTPRINT:
            await _insert_links(connection, LinkMethod.FOOTPRINT, query)
        official = (window.start, window.end)
        await connection.execute(
            load_sql("reconcile/repo_projects"),
            *official,
            MIN_WINDOW_COMMITS,
            MIN_LIKELY_COMMITS,
            hackathon.slug,
        )
        await connection.execute(
            load_sql("reconcile/account_projects"),
            *official,
            settings.friendbot_account,
            hackathon.slug,
        )
        await connection.execute(
            load_sql("reconcile/exclude_projects"),
            [f"repo:{name.lower()}" for name in hackathon.indexing().exclude_repos],
            hackathon.slug,
        )

    methods = await connection.fetch(
        load_sql("reconcile/report_methods"), hackathon.slug
    )
    footprints = await connection.fetch(
        load_sql("reconcile/report_footprints"), hackathon.slug
    )
    tiers = await connection.fetch(load_sql("reconcile/report_tiers"), hackathon.slug)
    return Report(
        links_by_method={row["method"]: row["n"] for row in methods},
        projects_by_footprint={row["footprint"]: row["n"] for row in footprints},
        projects_by_tier={row["tier"]: row["n"] for row in tiers},
    )


async def run_reconcile() -> None:
    await open_pool()
    async with pool().acquire() as connection:
        report = await reconcile(connection)
    log.info("%s", report.model_dump_json(indent=2))
