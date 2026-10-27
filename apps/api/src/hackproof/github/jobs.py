import asyncio
import logging

import httpx

from hackproof.config import get_settings
from hackproof.db import open_pool, pool
from hackproof.github.client import GithubClient
from hackproof.github.discovery import discover, read_seeds, store_candidates, wasm_meta_repos
from hackproof.github.models import Candidate
from hackproof.github.scan import Scanner, store_scan
from hackproof.hackathon import get_hackathon

log = logging.getLogger("hackproof.github")

SCAN_CONCURRENCY = 6


async def run_discover() -> None:
    settings, hackathon = get_settings(), get_hackathon()
    await open_pool()
    async with httpx.AsyncClient(timeout=30) as http:
        github = GithubClient(http, settings.github_tokens)
        async with pool().acquire() as connection:
            from_wasm = await wasm_meta_repos(connection)
        candidates = await discover(
            github,
            hackathon.window,
            hackathon.discovery,
            from_wasm,
            read_seeds(settings.seeds_file),
        )
    async with pool().acquire() as connection:
        await store_candidates(connection, candidates)
    log.info("stored %s candidate repos", len(candidates))


async def run_scan(force: bool) -> None:
    settings, hackathon = get_settings(), get_hackathon()
    await open_pool()
    async with pool().acquire() as connection:
        rows = await connection.fetch(
            """
            SELECT full_name, url, owner, default_branch, homepage FROM repos
            WHERE $1 OR scanned_at IS NULL ORDER BY pushed_at DESC NULLS LAST
            """,
            force,
        )
    repos = [Candidate(**row) for row in rows]
    log.info("scanning %s repos", len(repos))

    gate = asyncio.Semaphore(SCAN_CONCURRENCY)
    done = 0

    async with httpx.AsyncClient(timeout=30) as http:
        scanner = Scanner(
            GithubClient(http, settings.github_tokens), http, hackathon.window, hackathon.discovery
        )

        async def scan(repo: Candidate) -> None:
            nonlocal done
            async with gate:
                result = await scanner.scan(repo)
            if result is not None:
                async with pool().acquire() as connection:
                    await store_scan(connection, result)
            done += 1
            log.info("scanned %s/%s %s", done, len(repos), repo.full_name)

        await asyncio.gather(*(scan(repo) for repo in repos))
