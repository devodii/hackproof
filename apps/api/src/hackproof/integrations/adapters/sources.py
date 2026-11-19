from typing import Any

import httpx
from pydantic import BaseModel, ConfigDict, Field

from hackproof.integrations.catalog import ProfileContract
from hackproof.integrations.chain import ContractSnapshot


class Release(BaseModel):
    model_config = ConfigDict(extra="ignore")

    versions: dict[str, Any] = Field(default_factory=dict)
    time: dict[str, str] = Field(default_factory=dict)
    dist_tags: dict[str, str] = Field(default_factory=dict, alias="dist-tags")


class Repository(BaseModel):
    model_config = ConfigDict(extra="ignore")

    open_issues_count: int = 0
    stargazers_count: int = 0
    forks_count: int = 0
    pushed_at: str = ""
    archived: bool = False


async def observe_package(
    http: httpx.AsyncClient, contract: ProfileContract
) -> ContractSnapshot | None:
    registry = await http.get(
        f"https://registry.npmjs.org/{contract.id.replace('/', '%2F')}"
    )
    if registry.status_code != 200:
        return None
    release = Release.model_validate(registry.json())
    stamps = {
        version: stamp
        for version, stamp in release.time.items()
        if version not in {"created", "modified"}
    }
    latest_stamp = max(stamps.values()) if stamps else ""
    downloads = await http.get(
        f"https://api.npmjs.org/downloads/point/last-month/{contract.id}"
    )
    monthly = (
        downloads.json().get("downloads") if downloads.status_code == 200 else None
    )
    tags = ", ".join(f"{tag} {version}" for tag, version in release.dist_tags.items())
    return ContractSnapshot(
        facts={
            "tags": tags,
            "versions": len(release.versions),
            "published": latest_stamp[:10],
            "downloads_month": monthly,
        },
        items=sorted(release.versions)[-12:],
    )


async def observe_repo(
    http: httpx.AsyncClient, contract: ProfileContract
) -> ContractSnapshot | None:
    response = await http.get(
        f"https://api.github.com/repos/{contract.id}",
        headers={"Accept": "application/vnd.github+json"},
    )
    if response.status_code != 200:
        return None
    repository = Repository.model_validate(response.json())
    return ContractSnapshot(
        facts={
            "open_issues": repository.open_issues_count,
            "stars": repository.stargazers_count,
            "forks": repository.forks_count,
            "pushed": repository.pushed_at[:10],
            "archived": "TRUE" if repository.archived else "FALSE",
        }
    )
