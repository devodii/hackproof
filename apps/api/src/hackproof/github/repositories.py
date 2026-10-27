import asyncio
import json
import re
from collections.abc import Iterable
from typing import Any

from hackproof.github.client import GithubClient, GithubUnavailable
from hackproof.github.models import Candidate

FIELDS = """
  nameWithOwner url description stargazerCount forkCount isFork createdAt pushedAt homepageUrl
  primaryLanguage { name } licenseInfo { spdxId }
  defaultBranchRef { name } owner { login avatarUrl }
  repositoryTopics(first: 20) { nodes { topic { name } } }
"""
BATCH = 50
CONCURRENCY = 4
VALID_NAME = re.compile(r"^[\w.-]+/[\w.-]+$")


def candidate_from_node(node: dict[str, Any]) -> Candidate:
    branch = node["defaultBranchRef"]
    return Candidate(
        full_name=node["nameWithOwner"],
        url=node["url"],
        description=node["description"],
        stars=node["stargazerCount"],
        owner=node["owner"]["login"],
        owner_avatar=node["owner"]["avatarUrl"],
        default_branch=branch["name"] if branch else None,
        homepage=node["homepageUrl"] or None,
        language=node["primaryLanguage"]["name"] if node["primaryLanguage"] else None,
        license=node["licenseInfo"]["spdxId"] if node["licenseInfo"] else None,
        forks=node["forkCount"],
        created_at=node["createdAt"],
        pushed_at=node["pushedAt"],
        fork=node["isFork"],
        topics=[edge["topic"]["name"] for edge in node["repositoryTopics"]["nodes"]],
    )


def _lookup(index: int, name: str) -> str:
    owner, repo = name.split("/")
    return (
        f"r{index}: repository(owner: {json.dumps(owner)}, name: {json.dumps(repo)}) {{{FIELDS}}}"
    )


def _query(names: list[str]) -> str:
    return "query {" + " ".join(_lookup(i, name) for i, name in enumerate(names)) + "}"


async def fetch_repositories(github: GithubClient, names: Iterable[str]) -> list[Candidate]:
    unique = sorted({name for name in names if VALID_NAME.match(name)})
    batches = [unique[i : i + BATCH] for i in range(0, len(unique), BATCH)]
    gate = asyncio.Semaphore(CONCURRENCY)

    async def fetch(batch: list[str]) -> list[Candidate]:
        try:
            async with gate:
                data = await github.graphql(_query(batch))
        except GithubUnavailable:
            if len(batch) == 1:
                return []
            half = len(batch) // 2
            first, second = await asyncio.gather(fetch(batch[:half]), fetch(batch[half:]))
            return first + second
        return [candidate_from_node(node) for node in data.values() if node]

    return [c for found in await asyncio.gather(*(fetch(b) for b in batches)) for c in found]
