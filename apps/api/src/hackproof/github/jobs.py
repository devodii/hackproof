import asyncio
import logging

import httpx

from hackproof.config import get_settings
from hackproof.db import open_pool, pool
from hackproof.github.client import GithubClient, GithubUnavailable
from hackproof.github.discovery import discover, store_candidates, wasm_meta_repos
from hackproof.github.models import Candidate
from hackproof.github.profiles import resolve_profiles
from hackproof.github.repositories import fetch_repositories
from hackproof.github.scan import Scanner, store_scan
from hackproof.hackathon import get_hackathon

log = logging.getLogger("hackproof.github")

SCAN_CONCURRENCY = 20


async def run_discover(include_strings: bool) -> None:
    settings, hackathon = get_settings(), get_hackathon()
    await open_pool()
    async with httpx.AsyncClient(timeout=30) as http:
        github = GithubClient(http, settings.github_tokens)
        async with pool().acquire() as connection:
            from_wasm = await wasm_meta_repos(connection)
        stages = discover(
            github,
            hackathon.window,
            hackathon.discovery,
            from_wasm,
            include_strings,
        )
        async for candidates in stages:
            async with pool().acquire() as connection:
                await store_candidates(connection, candidates)
            log.info("stored %s candidate repos", len(candidates))


async def run_scan(force: bool) -> None:
    settings, hackathon = get_settings(), get_hackathon()
    await open_pool()
    limits = httpx.Limits(max_connections=200, max_keepalive_connections=50)
    async with httpx.AsyncClient(timeout=30, limits=limits) as http:
        github = GithubClient(http, settings.github_tokens)

        async with pool().acquire() as connection:
            names = [
                row["full_name"]
                for row in await connection.fetch(
                    "SELECT full_name FROM repos WHERE $1 OR scanned_at IS NULL", force
                )
            ]
            refreshed = await fetch_repositories(github, names, hackathon.window)
            await store_candidates(connection, refreshed)
            rows = await connection.fetch(
                """
                SELECT full_name, url, owner, default_branch, homepage, topics, base_sha
                FROM repos
                WHERE ($1 OR scanned_at IS NULL)
                  AND (COALESCE(window_commits, 0) > 0
                       OR 'wasm_meta' = ANY(discovered_via))
                ORDER BY pushed_at DESC NULLS LAST
                """,
                force,
            )
        repos = [Candidate(**row) for row in rows]
        log.info("scanning %s repos", len(repos))

        scanner = Scanner(github, http, hackathon.discovery)
        gate = asyncio.Semaphore(SCAN_CONCURRENCY)
        done = 0

        async def scan(repo: Candidate) -> None:
            nonlocal done
            try:
                async with gate:
                    result = await scanner.scan(repo)
            except GithubUnavailable:
                log.warning("skipped %s, github unreachable", repo.full_name)
                result = None
            except Exception:
                log.exception("skipped %s, scan failed", repo.full_name)
                result = None
            if result is not None:
                async with pool().acquire() as connection:
                    await store_scan(connection, result)
            done += 1
            log.info("scanned %s/%s %s", done, len(repos), repo.full_name)

        await asyncio.gather(*(scan(repo) for repo in repos))
        async with pool().acquire() as connection:
            resolved = await resolve_profiles(github, connection)
        log.info("resolved %s contributor profiles", resolved)
