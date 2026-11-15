import asyncio
from datetime import datetime
from pathlib import PurePosixPath

from hackproof.github.client import GithubClient
from hackproof.github.dependencies import MANIFESTS, SKIP_DIRECTORIES, fingerprint

MAX_MANIFESTS = 60


async def _stellar_packages_at(
    github: GithubClient, full_name: str, sha: str, wanted: dict[str, list[str]]
) -> dict[str, str | None]:
    tree = await github.json(f"/repos/{full_name}/git/trees/{sha}", {"recursive": "1"})
    paths = sorted(
        (
            entry["path"]
            for entry in (tree or {}).get("tree", [])
            if entry["type"] == "blob"
            and PurePosixPath(entry["path"]).name in MANIFESTS
            and not SKIP_DIRECTORIES & set(PurePosixPath(entry["path"]).parts[:-1])
        ),
        key=lambda path: (len(PurePosixPath(path).parts), path),
    )[:MAX_MANIFESTS]
    contents = await asyncio.gather(
        *(github.raw(full_name, sha, path) for path in paths)
    )
    manifests = {
        path: content.decode(errors="ignore")
        for path, content in zip(paths, contents, strict=True)
        if content
    }
    return fingerprint(manifests, wanted).packages


async def stellar_added_in_window(
    github: GithubClient,
    full_name: str,
    wanted: dict[str, list[str]],
    base_sha: str | None,
    window_end: datetime,
) -> bool:
    until = window_end.strftime("%Y-%m-%dT%H:%M:%SZ")
    commits = await github.json(
        f"/repos/{full_name}/commits", {"until": until, "per_page": 1}
    )
    if not commits:
        return False
    before = (
        await _stellar_packages_at(github, full_name, base_sha, wanted)
        if base_sha
        else {}
    )
    after = await _stellar_packages_at(github, full_name, commits[0]["sha"], wanted)
    return not before and bool(after)
