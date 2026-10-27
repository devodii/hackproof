import asyncio
import logging
from collections.abc import AsyncIterator, Awaitable, Callable
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import asyncpg

from hackproof.github.client import GithubClient, Search
from hackproof.github.models import Candidate
from hackproof.github.repositories import fetch_repositories
from hackproof.hackathon import Discovery, Window
from hackproof.linking.country import resolve_country
from hackproof.linking.repo_ref import normalize_repo

log = logging.getLogger("hackproof.discovery")

PAGE_SIZE = 100
RESULT_CAP = 1000
SIZE_CEILING = 400_000
PINNED_PREFIXES = ("seed:", "wasm_meta")

Count = Callable[[int, int], Awaitable[int]]


def is_pinned(candidate: Candidate) -> bool:
    return any(via.startswith(PINNED_PREFIXES) for via in candidate.discovered_via)


def should_keep(candidate: Candidate, window: Window, discovery: Discovery) -> bool:
    if is_pinned(candidate):
        return True
    if candidate.fork or candidate.owner.lower() in {o.lower() for o in discovery.exclude_owners}:
        return False
    return candidate.pushed_at is not None and candidate.pushed_at >= window.start - timedelta(
        days=1
    )


def parse_seeds(text: str) -> list[tuple[str, str]]:
    seeds = []
    for line in text.splitlines():
        parts = line.split()
        if not parts or parts[0].startswith("#"):
            continue
        full_name = normalize_repo(parts[0])
        if full_name:
            seeds.append((full_name, parts[1] if len(parts) > 1 else "manual"))
    return seeds


async def split_range(
    lo: int, hi: int, count: Count, cap: int = RESULT_CAP
) -> list[tuple[int, int]]:
    if lo >= hi or await count(lo, hi) <= cap:
        return [(lo, hi)]
    middle = (lo + hi) // 2
    left, right = await asyncio.gather(
        split_range(lo, middle, count, cap), split_range(middle + 1, hi, count, cap)
    )
    return left + right


def _stamp(seconds: int) -> str:
    return datetime.fromtimestamp(seconds, UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


async def _total(github: GithubClient, path: str, query: str, kind: Search) -> int:
    data = await github.json(path, {"q": query, "per_page": 1}, search=kind)
    return data["total_count"] if data else 0


async def repository_slices(
    github: GithubClient, query: str, since: datetime, until: datetime
) -> list[str]:
    async def count(lo: int, hi: int) -> int:
        pushed = f"pushed:{_stamp(lo)}..{_stamp(hi)}"
        return await _total(github, "/search/repositories", f"{query} {pushed}", "repositories")

    ranges = await split_range(int(since.timestamp()), int(until.timestamp()), count)
    return [f"{query} pushed:{_stamp(lo)}..{_stamp(hi)}" for lo, hi in ranges]


async def code_slices(github: GithubClient, query: str) -> list[str]:
    if await _total(github, "/search/code", query, "code") <= RESULT_CAP:
        return [query]

    async def count(lo: int, hi: int) -> int:
        return await _total(github, "/search/code", f"{query} size:{lo}..{hi}", "code")

    return [f"{query} size:{lo}..{hi}" for lo, hi in await split_range(0, SIZE_CEILING, count)]


async def _hits(github: GithubClient, path: str, query: str, kind: Search) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for page in range(1, RESULT_CAP // PAGE_SIZE + 1):
        data = await github.json(
            path, {"q": query, "per_page": PAGE_SIZE, "page": page}, search=kind
        )
        batch = data["items"] if data else []
        items.extend(batch)
        if len(batch) < PAGE_SIZE:
            break
    return items


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
            for item in await _hits(github, "/search/repositories", sliced, "repositories"):
                note(item["full_name"], f"search:{query}")
        log.info("repo search done: %s slices, %s", len(slices), query)

    async def code_query(query: str) -> None:
        slices = await code_slices(github, query)
        for sliced in slices:
            for item in await _hits(github, "/search/code", sliced, "code"):
                note(item["repository"]["full_name"], f"code:{query}")
        log.info("code search done: %s slices, %s", len(slices), query)

    await asyncio.gather(
        *(repository_query(q) for q in repository_queries),
        *(code_query(q) for q in code_queries),
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
    seeds: list[tuple[str, str]],
    include_strings: bool = False,
    now: datetime | None = None,
) -> AsyncIterator[list[Candidate]]:
    since, until = window.start - timedelta(days=1), now or datetime.now(UTC)
    pinned: dict[str, set[str]] = {}
    for name in wasm_meta_repos:
        pinned.setdefault(name.lower(), set()).add("wasm_meta")
    for name, tag in seeds:
        pinned.setdefault(name.lower(), set()).add(f"seed:{tag}")

    stages = [(discovery.github_queries, [], pinned), ([], discovery.github_code_queries, {})]
    if include_strings:
        stages.append(([], discovery.github_string_queries, {}))
    for repository_queries, code_queries, extra in stages:
        found = {name: set(vias) for name, vias in extra.items()}
        await _collect(github, found, repository_queries, code_queries, since, until)
        yield await _resolve(github, found, window, discovery)


async def store_candidates(connection: asyncpg.Connection, candidates: list[Candidate]) -> None:
    await connection.executemany(
        """
        INSERT INTO repos (full_name, url, description, stars, owner, owner_avatar,
                           default_branch, homepage, language, license, forks, created_at,
                           pushed_at, topics, window_commits, total_commits, base_sha,
                           owner_location, country, discovered_via)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16,
                $17, $18, $19, $20)
        ON CONFLICT (full_name) DO UPDATE SET
            description = EXCLUDED.description, stars = EXCLUDED.stars,
            default_branch = EXCLUDED.default_branch, homepage = EXCLUDED.homepage,
            language = EXCLUDED.language, license = EXCLUDED.license, forks = EXCLUDED.forks,
            pushed_at = EXCLUDED.pushed_at, topics = EXCLUDED.topics,
            window_commits = EXCLUDED.window_commits, total_commits = EXCLUDED.total_commits,
            base_sha = EXCLUDED.base_sha, owner_location = EXCLUDED.owner_location,
            country = EXCLUDED.country,
            discovered_via = ARRAY(
                SELECT DISTINCT via FROM unnest(repos.discovered_via || EXCLUDED.discovered_via) via
            )
        """,
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
            )
            for c in candidates
        ],
    )


async def wasm_meta_repos(connection: asyncpg.Connection) -> list[str]:
    rows = await connection.fetch(
        "SELECT DISTINCT source_repo FROM wasm_uploads WHERE source_repo IS NOT NULL"
    )
    return sorted({name for row in rows if (name := normalize_repo(row["source_repo"]))})


def read_seeds(path: Path) -> list[tuple[str, str]]:
    return parse_seeds(path.read_text()) if path.exists() else []
