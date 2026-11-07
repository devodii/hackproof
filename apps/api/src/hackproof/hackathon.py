from datetime import datetime, timedelta
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel

from hackproof.config import ROOT, get_settings

Place = Literal["first", "runner-up"]


class Window(BaseModel):
    start: datetime
    pull_start: datetime
    end: datetime


class Discovery(BaseModel):
    github_queries: list[str]
    github_code_queries: list[str]
    github_string_queries: list[str]
    dependency_fingerprints: dict[str, list[str]]
    exclude_owners: list[str]
    exclude_repos: list[str] = []
    known_infra_accounts: list[str]


class Award(BaseModel):
    project_id: str
    place: Place


class Hackathon(BaseModel):
    slug: str
    name: str
    window: Window
    awards: list[Award] = []
    discovery: Discovery


@lru_cache
def get_hackathon() -> Hackathon:
    with get_settings().hackathon_file.open() as file:
        return Hackathon.model_validate(yaml.safe_load(file))


def places() -> dict[str, Place]:
    return {award.project_id: award.place for award in get_hackathon().awards}


DEFAULT_CODE_QUERIES = [
    "soroban-sdk filename:Cargo.toml",
    "@stellar/stellar-sdk filename:package.json",
    "@stellar/freighter-api filename:package.json",
    "@creit.tech/stellar-wallets-kit filename:package.json",
    "stellar-base filename:package.json",
    "stellar-sdk filename:requirements.txt",
    "stellar-sdk filename:pyproject.toml",
    "github.com/stellar/go filename:go.mod",
]

DEFAULT_STRING_QUERIES = [
    "Test SDF Network ; September 2015",
    "soroban-testnet.stellar.org",
    "friendbot.stellar.org",
]

DEFAULT_FINGERPRINTS: dict[str, list[str]] = {
    "rust": ["soroban-sdk", "stellar-xdr", "stellar-strkey"],
    "js": [
        "@stellar/stellar-sdk",
        "@stellar/stellar-base",
        "@stellar/freighter-api",
        "@creit.tech/stellar-wallets-kit",
        "@stellar/typescript-wallet-sdk",
        "stellar-sdk",
        "stellar-base",
    ],
    "python": ["stellar-sdk", "stellar_sdk"],
    "go": ["github.com/stellar/go"],
}

DEFAULT_EXCLUDE_OWNERS = ["stellar", "stellar-expert", "soroban", "creit-tech", "stellar-light"]
DEFAULT_EXCLUDE_REPOS = ["stellar-scaffold/cli", "NethermindEth/stellar-private-payments"]


def _iso_utc(value: datetime) -> str:
    return value.strftime("%Y-%m-%dT%H:%M:%SZ")


def scaffold_hackathon(
    slug: str,
    name: str,
    start: str,
    end: str,
    pull_start: str | None = None,
    output_dir: Path | None = None,
) -> Path:
    parsed_start = datetime.fromisoformat(start.replace("Z", "+00:00"))
    parsed_end = datetime.fromisoformat(end.replace("Z", "+00:00"))
    parsed_pull = (
        datetime.fromisoformat(pull_start.replace("Z", "+00:00"))
        if pull_start
        else parsed_start - timedelta(hours=1)
    )
    keyword = slug.split("-")[0].lower()
    name_query = name.lower()
    github_queries = [
        f"{keyword} in:name,description,readme,topics",
        f'"{name_query}" in:name,description,readme',
        "stellar in:name,description,readme,topics",
        "soroban in:name,description,readme,topics",
        "stellar-sdk in:readme",
        "freighter in:description,readme",
        "topic:stellar",
        "topic:soroban",
        f"topic:{keyword}",
    ]
    payload: dict[str, Any] = {
        "slug": slug,
        "name": name,
        "window": {
            "start": _iso_utc(parsed_start),
            "pull_start": _iso_utc(parsed_pull),
            "end": _iso_utc(parsed_end),
        },
        "awards": [],
        "discovery": {
            "github_queries": github_queries,
            "github_code_queries": list(DEFAULT_CODE_QUERIES),
            "github_string_queries": list(DEFAULT_STRING_QUERIES),
            "dependency_fingerprints": dict(DEFAULT_FINGERPRINTS),
            "exclude_owners": list(DEFAULT_EXCLUDE_OWNERS),
            "exclude_repos": list(DEFAULT_EXCLUDE_REPOS),
            "known_infra_accounts": [],
        },
    }
    validated = Hackathon.model_validate(payload)
    target_dir = output_dir or (ROOT / "data")
    target_dir.mkdir(parents=True, exist_ok=True)
    path = target_dir / f"{validated.slug}.yaml"
    path.write_text(yaml.safe_dump(payload, sort_keys=False, allow_unicode=True, width=120))
    return path
