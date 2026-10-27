import asyncio
from datetime import timedelta
from pathlib import Path
from typing import Any

import asyncpg

from hackproof.github.client import GithubClient, Search
from hackproof.github.models import Candidate
from hackproof.hackathon import Discovery, Window
from hackproof.linking.repo_ref import normalize_repo

PAGE_SIZE = 100
MAX_PAGES = 10
PINNED_PREFIXES = ("seed:", "wasm_meta")


def candidate_from(item: dict[str, Any], vias: set[str]) -> Candidate:
    return Candidate(
        full_name=item["full_name"],
        url=item["html_url"],
        description=item.get("description"),
        stars=item.get("stargazers_count", 0),
        owner=item["owner"]["login"],
        owner_avatar=item["owner"].get("avatar_url"),
        default_branch=item.get("default_branch"),
        homepage=item.get("homepage") or None,
        created_at=item.get("created_at"),
        pushed_at=item.get("pushed_at"),
        fork=item.get("fork", False),
        discovered_via=vias,
    )


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


async def _search(
    github: GithubClient, path: str, query: str, kind: Search
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for page in range(1, MAX_PAGES + 1):
        data = await github.json(
            path, {"q": query, "per_page": PAGE_SIZE, "page": page}, search=kind
        )
        batch = data["items"] if data else []
        items.extend(batch)
        if len(batch) < PAGE_SIZE:
            break
    return items


def _add(found: dict[str, Candidate], candidate: Candidate) -> None:
    existing = found.setdefault(candidate.full_name, candidate)
    existing.discovered_via |= candidate.discovered_via


async def discover(
    github: GithubClient,
    window: Window,
    discovery: Discovery,
    wasm_meta_repos: list[str],
    seeds: list[tuple[str, str]],
) -> list[Candidate]:
    found: dict[str, Candidate] = {}
    named: dict[str, set[str]] = {}

    async def repository_query(query: str) -> None:
        for item in await _search(github, "/search/repositories", query, "repositories"):
            _add(found, candidate_from(item, {f"search:{query}"}))

    async def code_query(query: str) -> None:
        for item in await _search(github, "/search/code", query, "code"):
            named.setdefault(item["repository"]["full_name"], set()).add(f"code:{query}")

    await asyncio.gather(
        *(repository_query(q) for q in discovery.github_queries),
        *(code_query(q) for q in discovery.github_code_queries),
    )
    for name in wasm_meta_repos:
        named.setdefault(name, set()).add("wasm_meta")
    for name, tag in seeds:
        named.setdefault(name, set()).add(f"seed:{tag}")

    gate = asyncio.Semaphore(8)

    async def resolve(name: str, vias: set[str]) -> None:
        if name not in found:
            async with gate:
                item = await github.json(f"/repos/{name}")
            if item is None:
                return
            found[name] = candidate_from(item, set())
        found[name].discovered_via |= vias

    await asyncio.gather(*(resolve(name, vias) for name, vias in named.items()))
    return [c for c in found.values() if should_keep(c, window, discovery)]


async def store_candidates(connection: asyncpg.Connection, candidates: list[Candidate]) -> None:
    await connection.executemany(
        """
        INSERT INTO repos (full_name, url, description, stars, owner, owner_avatar,
                           default_branch, homepage, created_at, pushed_at, discovered_via)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
        ON CONFLICT (full_name) DO UPDATE SET
            description = EXCLUDED.description, stars = EXCLUDED.stars,
            default_branch = EXCLUDED.default_branch, homepage = EXCLUDED.homepage,
            pushed_at = EXCLUDED.pushed_at,
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
                c.created_at,
                c.pushed_at,
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
