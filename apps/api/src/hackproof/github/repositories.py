import asyncio
import json
import re
from collections.abc import Iterable
from typing import Any

from hackproof.github.client import GithubClient, GithubUnavailable
from hackproof.github.models import Candidate
from hackproof.hackathon import Window

FIELDS = """
  nameWithOwner url description stargazerCount forkCount isFork createdAt pushedAt homepageUrl
  primaryLanguage {{ name }} licenseInfo {{ spdxId }}
  defaultBranchRef {{
    name
    target {{ ... on Commit {{
      total: history {{ totalCount }}
      inWindow: history(since: "{start}", until: "{end}") {{ totalCount }}
      before: history(until: "{start}", first: 1) {{ nodes {{ oid }} }}
    }} }}
  }}
  owner {{ login avatarUrl ... on User {{ location }} ... on Organization {{ location }} }}
  repositoryTopics(first: 20) {{ nodes {{ topic {{ name }} }} }}
"""
BATCH = 50
CONCURRENCY = 4
VALID_NAME = re.compile(r"^[\w.-]+/[\w.-]+$")


def candidate_from_node(node: dict[str, Any]) -> Candidate:
    branch = node["defaultBranchRef"]
    commit = (branch or {}).get("target") or {}
    before = commit.get("before", {}).get("nodes", [])
    return Candidate(
        full_name=node["nameWithOwner"],
        url=node["url"],
        description=node["description"],
        stars=node["stargazerCount"],
        owner=node["owner"]["login"],
        owner_avatar=node["owner"]["avatarUrl"],
        owner_location=node["owner"].get("location"),
        default_branch=branch["name"] if branch else None,
        homepage=node["homepageUrl"] or None,
        language=node["primaryLanguage"]["name"] if node["primaryLanguage"] else None,
        license=node["licenseInfo"]["spdxId"] if node["licenseInfo"] else None,
        forks=node["forkCount"],
        total_commits=commit.get("total", {}).get("totalCount"),
        window_commits=commit.get("inWindow", {}).get("totalCount"),
        base_sha=before[0]["oid"] if before else None,
        created_at=node["createdAt"],
        pushed_at=node["pushedAt"],
        fork=node["isFork"],
        topics=[edge["topic"]["name"] for edge in node["repositoryTopics"]["nodes"]],
    )


def _lookup(index: int, name: str, fields: str) -> str:
    owner, repo = name.split("/")
    return (
        f"r{index}: repository(owner: {json.dumps(owner)}, name: {json.dumps(repo)}) {{{fields}}}"
    )


def _query(names: list[str], window: Window) -> str:
    fields = FIELDS.format(start=window.start.isoformat(), end=window.end.isoformat())
    return "query {" + " ".join(_lookup(i, name, fields) for i, name in enumerate(names)) + "}"


async def fetch_repositories(
    github: GithubClient, names: Iterable[str], window: Window
) -> list[Candidate]:
    unique = sorted({name for name in names if VALID_NAME.match(name)})
    batches = [unique[i : i + BATCH] for i in range(0, len(unique), BATCH)]
    gate = asyncio.Semaphore(CONCURRENCY)

    async def fetch(batch: list[str]) -> list[Candidate]:
        try:
            async with gate:
                data = await github.graphql(_query(batch, window))
        except GithubUnavailable:
            if len(batch) == 1:
                return []
            half = len(batch) // 2
            first, second = await asyncio.gather(fetch(batch[:half]), fetch(batch[half:]))
            return first + second
        return [candidate_from_node(node) for node in data.values() if node]

    return [c for found in await asyncio.gather(*(fetch(b) for b in batches)) for c in found]
