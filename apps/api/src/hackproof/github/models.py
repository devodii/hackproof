from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

RefKind = Literal["contract", "account", "asset", "wasm", "network"]


class Ref(BaseModel):
    model_config = ConfigDict(frozen=True)

    kind: RefKind
    value: str
    path: str


class DependencyFingerprint(BaseModel):
    ecosystems: list[str] = Field(default_factory=list)
    packages: dict[str, str | None] = Field(default_factory=dict)


class Candidate(BaseModel):
    full_name: str
    url: str
    description: str | None = None
    stars: int = 0
    owner: str
    owner_avatar: str | None = None
    default_branch: str | None = None
    homepage: str | None = None
    language: str | None = None
    license: str | None = None
    forks: int = 0
    created_at: datetime | None = None
    pushed_at: datetime | None = None
    fork: bool = False
    window_commits: int | None = None
    total_commits: int | None = None
    base_sha: str | None = None
    owner_location: str | None = None
    topics: list[str] = Field(default_factory=list)
    discovered_via: set[str] = Field(default_factory=set)


class Contributor(BaseModel):
    login: str
    url: str
    avatar_url: str | None = None
    contributions: int


class RepoScan(BaseModel):
    full_name: str
    refs: list[Ref]
    dependencies: DependencyFingerprint
    mentions_hackathon: bool
    stellar_added_in_window: bool | None
    contributors: list[Contributor]
