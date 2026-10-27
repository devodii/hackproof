import asyncio
import json

from hackproof.github.client import GithubClient, GithubUnavailable

BATCH = 25
CONCURRENCY = 6


def _query(full_name: str, ref: str, paths: list[str]) -> str:
    owner, repo = full_name.split("/")
    objects = " ".join(
        f"f{index}: object(expression: {json.dumps(f'{ref}:{path}')}) {{ ... on Blob {{ text }} }}"
        for index, path in enumerate(paths)
    )
    target = f"owner: {json.dumps(owner)}, name: {json.dumps(repo)}"
    return f"query {{ repository({target}) {{ {objects} }} }}"


async def fetch_texts(
    github: GithubClient, full_name: str, ref: str, paths: list[str]
) -> dict[str, str]:
    gate = asyncio.Semaphore(CONCURRENCY)

    async def fetch(batch: list[str]) -> dict[str, str]:
        try:
            async with gate:
                data = await github.graphql(_query(full_name, ref, batch))
        except GithubUnavailable:
            if len(batch) == 1:
                raise
            half = len(batch) // 2
            first, second = await asyncio.gather(fetch(batch[:half]), fetch(batch[half:]))
            return first | second
        repository = data["repository"] or {}
        return {
            path: blob["text"]
            for index, path in enumerate(batch)
            if (blob := repository.get(f"f{index}")) and blob.get("text")
        }

    batches = [paths[i : i + BATCH] for i in range(0, len(paths), BATCH)]
    merged: dict[str, str] = {}
    for found in await asyncio.gather(*(fetch(batch) for batch in batches)):
        merged |= found
    return merged
