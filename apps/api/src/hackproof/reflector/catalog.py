import re
from functools import lru_cache
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, PrivateAttr

from hackproof.config import get_settings

Network = Literal["testnet", "mainnet"]
AssetKind = Literal["stellar", "other"]
SignalGroup = Literal["client", "read", "safety", "risk"]


class NetworkConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rpc_url: str
    passphrase: str
    explorer: str


class Feed(BaseModel):
    model_config = ConfigDict(extra="forbid")

    slug: str
    name: str
    network: Network
    source: str
    asset_kind: AssetKind
    contract_id: str


class LiveAsset(BaseModel):
    model_config = ConfigDict(extra="forbid")

    feed: str
    asset: str


class Signal(BaseModel):
    model_config = ConfigDict(extra="forbid")

    slug: str
    group: SignalGroup
    label: str
    patterns: list[str]

    _regexes: list[re.Pattern[str]] = PrivateAttr(default_factory=list)

    def model_post_init(self, _: object) -> None:
        self._regexes = [re.compile(pattern) for pattern in self.patterns]

    @property
    def regexes(self) -> list[re.Pattern[str]]:
        return self._regexes


class Oracle(BaseModel):
    model_config = ConfigDict(extra="forbid")

    slug: str
    name: str
    patterns: list[str]

    _regexes: list[re.Pattern[str]] = PrivateAttr(default_factory=list)

    def model_post_init(self, _: object) -> None:
        self._regexes = [
            re.compile(pattern, re.IGNORECASE) for pattern in self.patterns
        ]

    @property
    def regexes(self) -> list[re.Pattern[str]]:
        return self._regexes


class Tickers(BaseModel):
    model_config = ConfigDict(extra="forbid")

    patterns: list[str]

    _regexes: list[re.Pattern[str]] = PrivateAttr(default_factory=list)

    def model_post_init(self, _: object) -> None:
        self._regexes = [re.compile(pattern) for pattern in self.patterns]

    @property
    def regexes(self) -> list[re.Pattern[str]]:
        return self._regexes


class ReflectorCatalog(BaseModel):
    model_config = ConfigDict(extra="forbid")

    age_factor: int
    networks: dict[Network, NetworkConfig]
    feeds: list[Feed]
    live: list[LiveAsset]
    packages: dict[str, list[str]]
    signals: list[Signal]
    tickers: Tickers
    oracles: list[Oracle]
    by_contract: dict[str, Feed] = Field(default_factory=dict, exclude=True)

    def model_post_init(self, _: object) -> None:
        self.by_contract = {feed.contract_id: feed for feed in self.feeds}

    def feed(self, slug: str) -> Feed:
        return next(feed for feed in self.feeds if feed.slug == slug)


@lru_cache
def get_reflector() -> ReflectorCatalog:
    with get_settings().reflector_file.open() as file:
        return ReflectorCatalog.model_validate(yaml.safe_load(file))
