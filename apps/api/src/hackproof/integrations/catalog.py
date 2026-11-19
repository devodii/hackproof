import re
from functools import lru_cache
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, PrivateAttr

from hackproof.config import get_settings


class Network(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rpc_url: str
    passphrase: str
    explorer: str


class ProfileContract(BaseModel):
    model_config = ConfigDict(extra="forbid")

    slug: str
    id: str
    name: str
    network: str
    kind: str
    url: str | None = None
    attributes: dict[str, str] = Field(default_factory=dict)


class Patterned(BaseModel):
    model_config = ConfigDict(extra="forbid")

    slug: str
    label: str
    patterns: list[str]
    _regexes: list[re.Pattern[str]] = PrivateAttr(default_factory=list)

    def model_post_init(self, _: object) -> None:
        self._regexes = [re.compile(pattern) for pattern in self.patterns]

    @property
    def regexes(self) -> list[re.Pattern[str]]:
        return self._regexes


class Signal(Patterned):
    group: str


class Capture(Patterned):
    pass


class Check(BaseModel):
    model_config = ConfigDict(extra="forbid")

    slug: str
    label: str
    severity: Literal["warn", "fail"]
    requires: list[str] = Field(default_factory=list)
    missing: list[str] = Field(default_factory=list)
    forbids: list[str] = Field(default_factory=list)
    only_networks: list[str] = Field(default_factory=list)


class LiveProbe(BaseModel):
    model_config = ConfigDict(extra="forbid")

    contract: str
    asset: str


class Profile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    adapter: str | None = None
    params: dict[str, int] = Field(default_factory=dict)
    hints: list[str] = Field(default_factory=list)
    networks: dict[str, Network] = Field(default_factory=dict)
    context: list[str]
    contracts: list[ProfileContract] = Field(default_factory=list)
    surfaces: list[ProfileContract] = Field(default_factory=list)
    live: list[LiveProbe] = Field(default_factory=list)
    signals: list[Signal] = Field(default_factory=list)
    captures: list[Capture] = Field(default_factory=list)
    checks: list[Check] = Field(default_factory=list)
    _context: list[re.Pattern[str]] = PrivateAttr(default_factory=list)

    def model_post_init(self, _: object) -> None:
        self._context = [re.compile(pattern, re.IGNORECASE) for pattern in self.context]

    def in_context(self, text: str) -> bool:
        return any(pattern.search(text) for pattern in self._context)

    def contract(self, slug: str) -> ProfileContract:
        return next(item for item in self.contracts if item.slug == slug)


class Product(BaseModel):
    slug: str
    name: str
    site: str
    packages: dict[str, list[str]] = Field(default_factory=dict)
    endpoints: list[str] = Field(default_factory=list)
    github_owners: list[str] = Field(default_factory=list)
    profile: Profile | None = None


class Partner(Product):
    category: str


class Tool(Product):
    pass


class Agent(BaseModel):
    slug: str
    name: str
    site: str
    files: list[str] = Field(default_factory=list)
    authors: list[str] = Field(default_factory=list)


class Catalog(BaseModel):
    partners: list[Partner]
    tools: list[Tool] = Field(default_factory=list)
    agents: list[Agent] = Field(default_factory=list)

    def partner(self, slug: str) -> Partner:
        return next(partner for partner in self.partners if partner.slug == slug)

    def deep(self, slug: str) -> Product | None:
        found = next(
            (item for item in [*self.partners, *self.tools] if item.slug == slug), None
        )
        return found if found and found.profile else None


@lru_cache
def get_catalog() -> Catalog:
    with get_settings().integrations_file.open() as file:
        return Catalog.model_validate(yaml.safe_load(file))
