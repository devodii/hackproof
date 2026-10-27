import logging

import httpx

from hackproof.config import get_settings
from hackproof.db import open_pool, pool
from hackproof.linking.country import resolve_country
from hackproof.linking.github import GithubClient
from hackproof.linking.repo_ref import normalize_repo

log = logging.getLogger("hackproof.link")


async def link_wasm_to_repos() -> int:
    async with pool().acquire() as connection:
        rows = await connection.fetch(
            "SELECT DISTINCT wasm_hash, source_repo FROM wasm_uploads WHERE source_repo IS NOT NULL"
        )
        linked = [
            (row["wasm_hash"], full_name, "wasm-meta")
            for row in rows
            if (full_name := normalize_repo(row["source_repo"]))
        ]
        await connection.executemany(
            "INSERT INTO wasm_repos VALUES ($1, $2, $3) ON CONFLICT DO NOTHING", linked
        )
    return len(linked)


async def enrich_repos(client: httpx.AsyncClient) -> int:
    github = GithubClient(client, get_settings().github_token)
    async with pool().acquire() as connection:
        names = [
            row["full_name"]
            for row in await connection.fetch(
                "SELECT DISTINCT full_name FROM wasm_repos "
                "WHERE full_name NOT IN (SELECT full_name FROM repos)"
            )
        ]
        found = 0
        for name in names:
            repo = await github.repo(name)
            if repo is None:
                log.info("skipped %s", name)
                continue
            await connection.execute(
                "INSERT INTO repos VALUES ($1, $2, $3, $4, $5, $6, $7, $8) ON CONFLICT DO NOTHING",
                repo.full_name,
                repo.url,
                repo.description,
                repo.stars,
                repo.owner,
                repo.owner_avatar,
                repo.owner_location,
                resolve_country(repo.owner_location),
            )
            found += 1
    return found


async def run_link() -> None:
    await open_pool()
    linked = await link_wasm_to_repos()
    log.info("linked %s wasm hashes to repos", linked)
    async with httpx.AsyncClient(timeout=30) as client:
        enriched = await enrich_repos(client)
    log.info("enriched %s repos from github", enriched)
