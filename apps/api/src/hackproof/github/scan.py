import asyncio
import hashlib
import re
from pathlib import PurePosixPath

import asyncpg
import httpx

from hackproof.github.client import GithubClient
from hackproof.github.commits import count_commits
from hackproof.github.demo import scan_demo
from hackproof.github.dependencies import MANIFESTS, fingerprint
from hackproof.github.history import stellar_added_in_window
from hackproof.github.models import Candidate, Ref, RepoScan
from hackproof.github.refs import extract_refs
from hackproof.hackathon import Discovery, Window
from hackproof.linking.country import resolve_country

TEXT_SUFFIXES = {
    ".rs", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".py", ".go", ".toml", ".json",
    ".md", ".yml", ".yaml", ".sh", ".txt", ".html", ".env", ".sol", ".vue", ".svelte",
}  # fmt: skip
SKIP_DIRECTORIES = {"node_modules", "dist", "target", ".git", "build", "vendor", ".next"}
SKIP_FILES = {"package-lock.json", "pnpm-lock.yaml", "yarn.lock", "Cargo.lock", "poetry.lock"}
FILE_CONCURRENCY = 100
MAX_TEXT_FILES = 60
MAX_WASM_FILES = 5
MAX_TEXT_BYTES = 512_000
MAX_WASM_BYTES = 5_000_000
HACKATHON_MENTION = re.compile(r"hack\s?meridian|meridian\s+2026", re.IGNORECASE)
HACKATHON_TOPIC = re.compile(r"hack-?meridian", re.IGNORECASE)
DEMO_URL = re.compile(
    r"https?://[\w.-]+\.(?:vercel\.app|netlify\.app|pages\.dev|github\.io|fly\.dev|onrender\.com)\S*"
)


def _is_text(path: str) -> bool:
    name = PurePosixPath(path).name
    return (
        PurePosixPath(path).suffix in TEXT_SUFFIXES or name in MANIFESTS or name.startswith(".env")
    )


def _priority(path: str) -> tuple[int, int, str]:
    name = PurePosixPath(path).name
    important = name in MANIFESTS or name.lower().startswith("readme") or name.startswith(".env")
    return (0 if important else 1, len(PurePosixPath(path).parts), path)


def select_files(entries: list[dict]) -> tuple[list[str], list[str]]:
    texts: list[str] = []
    wasms: list[str] = []
    for entry in entries:
        if entry["type"] != "blob":
            continue
        path = entry["path"]
        parts = PurePosixPath(path).parts
        name = parts[-1]
        directories = set(parts[:-1])
        size = entry.get("size", 0)
        if name.endswith(".wasm"):
            if size <= MAX_WASM_BYTES and not {"node_modules", ".git"} & directories:
                wasms.append(path)
        elif (
            _is_text(path)
            and size <= MAX_TEXT_BYTES
            and not SKIP_DIRECTORIES & directories
            and name not in SKIP_FILES
            and not name.endswith(".min.js")
        ):
            texts.append(path)
    return sorted(texts, key=_priority)[:MAX_TEXT_FILES], wasms[:MAX_WASM_FILES]


class Scanner:
    def __init__(
        self, github: GithubClient, http: httpx.AsyncClient, window: Window, discovery: Discovery
    ) -> None:
        self._github = github
        self._http = http
        self._window = window
        self._discovery = discovery
        self._locations: dict[str, str | None] = {}
        self._files = asyncio.Semaphore(FILE_CONCURRENCY)

    async def _text(self, repo: Candidate, branch: str, path: str) -> tuple[str, str]:
        async with self._files:
            content = await self._github.raw(repo.full_name, branch, path)
        return path, content.decode(errors="ignore") if content else ""

    async def _wasm_ref(self, repo: Candidate, branch: str, path: str) -> Ref | None:
        async with self._files:
            content = await self._github.raw(repo.full_name, branch, path, limit=MAX_WASM_BYTES)
        if content is None:
            return None
        return Ref(kind="wasm", value=hashlib.sha256(content).hexdigest(), path=path)

    async def _owner_location(self, owner: str) -> str | None:
        if owner not in self._locations:
            profile = await self._github.json(f"/users/{owner}")
            self._locations[owner] = profile.get("location") if profile else None
        return self._locations[owner]

    async def scan(self, repo: Candidate) -> RepoScan | None:
        branch = repo.default_branch or "HEAD"
        tree = await self._github.json(
            f"/repos/{repo.full_name}/git/trees/{branch}", {"recursive": "1"}
        )
        if tree is None:
            return None
        text_paths, wasm_paths = select_files(tree["tree"])
        texts, wasms, window_commits, total_commits, location = await asyncio.gather(
            asyncio.gather(*(self._text(repo, branch, path) for path in text_paths)),
            asyncio.gather(*(self._wasm_ref(repo, branch, path) for path in wasm_paths)),
            count_commits(
                self._github,
                repo.full_name,
                since=self._window.start.isoformat(),
                until=self._window.end.isoformat(),
            ),
            count_commits(self._github, repo.full_name),
            self._owner_location(repo.owner),
        )
        files = dict(texts)
        refs = [ref for path, text in files.items() for ref in extract_refs(text, path)]
        refs.extend(ref for ref in wasms if ref)
        readme = next((text for path, text in files.items() if _is_readme(path)), "")
        demo = repo.homepage or (match[0] if (match := DEMO_URL.search(readme)) else None)
        if demo:
            refs.extend(await scan_demo(self._http, demo))
        wanted = self._discovery.dependency_fingerprints
        dependencies = fingerprint(files, wanted)
        added = (
            await stellar_added_in_window(self._github, repo.full_name, files, wanted, self._window)
            if dependencies.packages
            else None
        )
        return RepoScan(
            full_name=repo.full_name,
            refs=list(dict.fromkeys(refs)),
            dependencies=dependencies,
            window_commits=window_commits,
            total_commits=total_commits,
            mentions_hackathon=bool(HACKATHON_MENTION.search(readme))
            or any(HACKATHON_TOPIC.search(topic) for topic in repo.topics),
            stellar_added_in_window=added,
            owner_location=location,
        )


def _is_readme(path: str) -> bool:
    return PurePosixPath(path).name.lower().startswith("readme")


async def store_scan(connection: asyncpg.Connection, scan: RepoScan) -> None:
    async with connection.transaction():
        await connection.executemany(
            "INSERT INTO repo_refs VALUES ($1, $2, $3, $4) ON CONFLICT DO NOTHING",
            [(scan.full_name, ref.kind, ref.value, ref.path) for ref in scan.refs],
        )
        await connection.execute(
            """
            UPDATE repos SET dependencies = $2, window_commits = $3, total_commits = $4,
                mentions_hackathon = $5, stellar_added_in_window = $8, owner_location = $6,
                country = $7, scanned_at = now()
            WHERE full_name = $1
            """,
            scan.full_name,
            scan.dependencies.model_dump(),
            scan.window_commits,
            scan.total_commits,
            scan.mentions_hackathon,
            scan.owner_location,
            resolve_country(scan.owner_location),
            scan.stellar_added_in_window,
        )
