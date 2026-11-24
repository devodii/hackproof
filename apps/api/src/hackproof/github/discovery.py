import asyncio
import logging
from collections.abc import AsyncIterator
from datetime import UTC, datetime, timedelta

import asyncpg
from trawl.github.client import GithubClient
from trawl.github.refs import normalize_repo
from trawl.github.search import code_slices, hits, patient, repository_slices

from hackproof.github.models import Candidate
from hackproof.github.repositories import fetch_repositories
from hackproof.hackathon import Discovery, Window
from hackproof.linking.country import resolve_country
from hackproof.sql_loader import load_sql

log = logging.getLogger("hackproof.discovery")

PINNED_VIA = "wasm_meta"


def is_pinned(candidate: Candidate) -> bool:
    return PINNED_VIA in candidate.discovered_via


def should_keep(candidate: Candidate, window: Window, discovery: Discovery) -> bool:
    if candidate.full_name.lower() in {
        name.lower() for name in discovery.exclude_repos
    }:
        return False
    if is_pinned(candidate):
        return True
    if candidate.fork or candidate.owner.lower() in {
        o.lower() for o in discovery.exclude_owners
    }:
        return False
    return (
        candidate.pushed_at is not None
        and candidate.pushed_at >= window.start - timedelta(days=1)
    )


async def _collect(
    github: GithubClient,
    found: dict[str, set[str]],
    repository_queries: list[str],
    code_queries: list[str],
    since: datetime,
    until: datetime,
) -> None:
    def note(name: str, via: str) -> None:
        found.setdefault(name.lower(), set()).add(via)

    async def repository_query(query: str) -> None:
        slices = await repository_slices(github, query, since, until)
        for sliced in slices:
            for item in await hits(
                github, "/search/repositories", sliced, "repositories"
            ):
                note(item["full_name"], f"search:{query}")
        log.info("repo search done: %s slices, %s", len(slices), query)

    async def code_query(query: str) -> None:
        slices = await code_slices(github, query)
        for sliced in slices:
            for item in await hits(github, "/search/code", sliced, "code"):
                note(item["repository"]["full_name"], f"code:{query}")
        log.info("code search done: %s slices, %s", len(slices), query)

    await asyncio.gather(
        *(patient(q, repository_query) for q in repository_queries),
        *(patient(q, code_query) for q in code_queries),
    )


async def _resolve(
    github: GithubClient,
    found: dict[str, set[str]],
    window: Window,
    discovery: Discovery,
) -> list[Candidate]:
    log.info("%s unique repos found, looking them up", len(found))
    candidates = await fetch_repositories(github, found, window)
    for candidate in candidates:
        candidate.discovered_via = found[candidate.full_name.lower()]
    kept = [c for c in candidates if should_keep(c, window, discovery)]
    log.info("%s of them pushed recently", len(kept))
    return kept


async def discover(
    github: GithubClient,
    window: Window,
    discovery: Discovery,
    wasm_meta_repos: list[str],
    include_strings: bool = False,
    now: datetime | None = None,
) -> AsyncIterator[list[Candidate]]:
    since, until = window.start - timedelta(days=1), now or datetime.now(UTC)
    pinned: dict[str, set[str]] = {}
    for name in wasm_meta_repos:
        pinned.setdefault(name.lower(), set()).add("wasm_meta")

    stages = [
        (discovery.github_queries, [], pinned),
        ([], discovery.github_code_queries, {}),
    ]
    if include_strings:
        stages.append(([], discovery.github_string_queries, {}))
    for repository_queries, code_queries, extra in stages:
        found = {name: set(vias) for name, vias in extra.items()}
        await _collect(github, found, repository_queries, code_queries, since, until)
        yield await _resolve(github, found, window, discovery)


async def store_candidates(
    connection: asyncpg.Connection, candidates: list[Candidate], hackathon: str
) -> None:
    await connection.executemany(
        load_sql("github/upsert_repo"),
        [
            (
                c.full_name,
                c.url,
                c.description,
                c.stars,
                c.owner,
                c.owner_avatar,
                c.default_branch,
                c.homepage,
                c.language,
                c.license,
                c.forks,
                c.created_at,
                c.pushed_at,
                c.topics,
                c.window_commits,
                c.total_commits,
                c.base_sha,
                c.owner_location,
                resolve_country(c.owner_location),
                sorted(c.discovered_via),
                hackathon,
            )
            for c in candidates
        ],
    )


async def wasm_meta_repos(connection: asyncpg.Connection) -> list[str]:
    rows = await connection.fetch(load_sql("github/wasm_source_repos"))
    return sorted(
        {name for row in rows if (name := normalize_repo(row["source_repo"]))}
    )
