import asyncio
from pathlib import PurePosixPath

from hackproof.github.client import GithubClient
from hackproof.github.dependencies import MANIFESTS, fingerprint


async def stellar_added_in_window(
    github: GithubClient,
    full_name: str,
    files: dict[str, str],
    wanted: dict[str, list[str]],
    base_sha: str | None,
) -> bool:
    if base_sha is None:
        return True
    manifests = [path for path in files if PurePosixPath(path).name in MANIFESTS]
    contents = await asyncio.gather(*(github.raw(full_name, base_sha, path) for path in manifests))
    earlier = {
        path: content.decode(errors="ignore")
        for path, content in zip(manifests, contents, strict=True)
        if content
    }
    return not fingerprint(earlier, wanted).packages
