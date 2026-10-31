import re
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import yaml

from hackproof.hackathon import Hackathon


def parse_datetime(value: str) -> datetime:
    """Parse ISO datetime string, ensuring timezone awareness (default UTC)."""
    cleaned = value.strip().strip("'\"")
    if re.match(r"^\d{4}-\d{2}-\d{2}$", cleaned):
        cleaned = f"{cleaned}T00:00:00Z"

    iso_str = cleaned.replace("Z", "+00:00")
    dt = datetime.fromisoformat(iso_str)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt


def format_iso(dt: datetime) -> str:
    """Format datetime as UTC ISO string ending in Z."""
    utc_dt = dt.astimezone(UTC)
    return utc_dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def build_default_discovery(slug: str, name: str) -> dict[str, Any]:
    slug_clean = slug.strip().lower()
    name_clean = name.strip()

    github_queries = [
        f"{slug_clean} in:name,description,readme,topics",
        f'"{name_clean}" in:name,description,readme',
        f"topic:{slug_clean}",
        "stellar in:name,description,readme,topics",
        "soroban in:name,description,readme,topics",
        "stellar-sdk in:readme",
        "freighter in:description,readme",
        "topic:stellar",
        "topic:soroban",
    ]

    seen: set[str] = set()
    deduped_github_queries: list[str] = []
    for q in github_queries:
        if q not in seen:
            seen.add(q)
            deduped_github_queries.append(q)

    github_code_queries = [
        "soroban-sdk filename:Cargo.toml",
        "@stellar/stellar-sdk filename:package.json",
        "@stellar/freighter-api filename:package.json",
        "@creit.tech/stellar-wallets-kit filename:package.json",
        "stellar-base filename:package.json",
        "stellar-sdk filename:requirements.txt",
        "stellar-sdk filename:pyproject.toml",
        "github.com/stellar/go filename:go.mod",
        '"@trustless-work/escrow filename:package.json"',
        '"@trustless-work/blocks filename:package.json"',
        '"@trustless-work/skill filename:package.json"',
        '"@privy-io/react-auth filename:package.json"',
        '"@privy-io/node filename:package.json"',
        '"@privy-io/server-auth filename:package.json"',
        '"passkey-kit filename:package.json"',
        '"@dfns/sdk filename:package.json"',
        '"@soroswap/sdk filename:package.json"',
        '"soroswap-library filename:Cargo.toml"',
        '"@defindex/sdk filename:package.json"',
        '"@blend-capital/blend-sdk filename:package.json"',
        '"blend-contract-sdk filename:Cargo.toml"',
        '"@stellar-broker/client filename:package.json"',
        '"@allbridge/bridge-core-sdk filename:package.json"',
        '"@circle-fin/bridge-kit filename:package.json"',
        '"@layerzerolabs/lz-v2-utilities filename:package.json"',
        '"@defuse-protocol/intents-sdk filename:package.json"',
        '"@defuse-protocol/one-click-sdk-typescript filename:package.json"',
        '"@axelar-network/axelarjs-sdk filename:package.json"',
        '"stellar-axelar-std filename:Cargo.toml"',
    ]

    github_string_queries = [
        "Test SDF Network ; September 2015",
        "soroban-testnet.stellar.org",
        "friendbot.stellar.org",
        "api.trustlesswork.com",
        "dev.api.trustlesswork.com",
        "auth.privy.io",
        "api.privy.io",
        "api.soroswap.finance",
        "api.defindex.io",
        "api.stellar.broker",
        "api.circle.com",
        "1click.chaindefuser.com",
    ]

    dependency_fingerprints = {
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

    exclude_owners = ["stellar", "stellar-expert", "soroban", "creit-tech", "stellar-light"]

    return {
        "github_queries": deduped_github_queries,
        "github_code_queries": github_code_queries,
        "github_string_queries": github_string_queries,
        "dependency_fingerprints": dependency_fingerprints,
        "exclude_owners": exclude_owners,
        "known_infra_accounts": [],
    }


def create_hackathon_config(
    slug: str,
    name: str,
    start_str: str,
    end_str: str,
    pull_start_str: str | None = None,
    output_path: Path | None = None,
) -> Path:
    start_dt = parse_datetime(start_str)
    end_dt = parse_datetime(end_str)
    if end_dt <= start_dt:
        raise ValueError(f"Window end ({end_str}) must be after window start ({start_str})")

    if pull_start_str:
        pull_start_dt = parse_datetime(pull_start_str)
    else:
        pull_start_dt = start_dt - timedelta(hours=1)

    raw_dict = {
        "slug": slug,
        "name": name,
        "window": {
            "start": format_iso(start_dt),
            "pull_start": format_iso(pull_start_dt),
            "end": format_iso(end_dt),
        },
        "awards": [],
        "discovery": build_default_discovery(slug, name),
    }

    # Validate against Hackathon pydantic model
    Hackathon.model_validate(raw_dict)

    if output_path is None:
        output_path = Path("config") / f"{slug}.yaml"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(raw_dict, f, sort_keys=False, allow_unicode=True)

    return output_path


def run_new_hackathon_interactive(
    slug: str | None = None,
    name: str | None = None,
    start: str | None = None,
    end: str | None = None,
    pull_start: str | None = None,
    output: str | None = None,
) -> Path:
    if not slug:
        slug = input("Hackathon slug (e.g. hackmeridian-2026): ").strip()
    if not name:
        name = input("Hackathon name (e.g. HackMeridian 2026): ").strip()
    if not start:
        start = input("Window start ISO datetime (e.g. 2026-10-25T09:00:00Z): ").strip()
    if not end:
        end = input("Window end ISO datetime (e.g. 2026-10-26T12:00:00Z): ").strip()

    output_path = Path(output) if output else None
    dest = create_hackathon_config(
        slug=slug,
        name=name,
        start_str=start,
        end_str=end,
        pull_start_str=pull_start,
        output_path=output_path,
    )

    print(f"\n[OK] Hackathon configuration created at: {dest}")
    print("\nNext commands to run:")
    print(f"  export HACKPROOF_HACKATHON_FILE={dest}")
    print("  hackproof sync")
    print("  hackproof discover")
    print("  hackproof scan")
    print("  hackproof reconcile")
    print("  hackproof export")

    return dest
