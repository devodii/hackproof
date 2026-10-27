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
    created_at: datetime | None = None
    pushed_at: datetime | None = None
    fork: bool = False
    discovered_via: set[str] = Field(default_factory=set)


class RepoScan(BaseModel):
    full_name: str
    refs: list[Ref]
    dependencies: DependencyFingerprint
    window_commits: int | None
    total_commits: int | None
    mentions_hackathon: bool
    owner_location: str | None
