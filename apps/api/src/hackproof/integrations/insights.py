import time
from collections import defaultdict
from datetime import datetime
from typing import Any

import httpx
from pydantic import BaseModel, ConfigDict

from hackproof.db import pool
from hackproof.indexer.rpc import SorobanRpc
from hackproof.integrations.adapters import ADAPTERS
from hackproof.integrations.catalog import Network, Product, get_catalog
from hackproof.integrations.chain import ContractSnapshot, Reading
from hackproof.integrations.profile import IntegrationProfile, build_profile
from hackproof.sql_loader import load_sql

NETWORK = "testnet"
LIVE_TTL = 30


class Model(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ContractState(Model):
    slug: str
    id: str
    name: str
    network: str
    kind: str
    attributes: dict[str, str]
    explorer_url: str
    snapshot: ContractSnapshot | None
    observed_at: datetime | None
    projects: int
    expired: list[str]


class Adopter(Model):
    project_id: str
    full_name: str
    url: str
    owner: str
    owner_avatar: str | None
    tier: str
    language: str | None
    profile: IntegrationProfile


class SignalCount(Model):
    slug: str
    label: str
    group: str
    projects: int


class CheckCount(Model):
    slug: str
    label: str
    severity: str
    passing: int
    failing: int


class CaptureCount(Model):
    value: str
    projects: int
    offered_by: list[str]
    expired_on: list[str]


class Overlap(Model):
    total: int
    matched: int
    by_contract: dict[str, int]


class IntegrationDetail(Model):
    slug: str
    name: str
    category: str
    site: str
    networks: dict[str, Network]
    contracts: list[ContractState]
    adopters: list[Adopter]
    of_projects: int
    signals: list[SignalCount]
    checks: list[CheckCount]
    captures: dict[str, list[CaptureCount]]
    overlap: Overlap | None
    live: list[str]


def _expired(snapshot: ContractSnapshot | None) -> list[str]:
    if snapshot is None:
        return []
    now = time.time()
    return [item for item, due in snapshot.deadlines.items() if due < now]


def _explorer(partner: Product, network: str, contract_id: str) -> str:
    assert partner.profile
    return f"{partner.profile.networks[network].explorer}/{contract_id}"


async def fetch_detail(partner: Product) -> IntegrationDetail:
    profile = partner.profile
    assert profile
    async with pool().acquire() as connection:
        rows = await connection.fetch(load_sql("integrations/adopters"), partner.slug)
        states = await connection.fetch(
            load_sql("integrations/contracts"), partner.slug
        )
        overlap_rows = await connection.fetch(
            load_sql("integrations/overlap"), partner.slug
        )
        total = (await connection.fetchrow(load_sql("integrations/project_total")))[
            "total"
        ]
    by_project: dict[str, list[Any]] = defaultdict(list)
    for row in rows:
        by_project[row["project_id"]].append(row)
    adopters: list[Adopter] = []
    for project_id, evidence in by_project.items():
        built = build_profile(
            partner, [(row["method"], row["evidence"]) for row in evidence], NETWORK
        )
        first = evidence[0]
        adopters.append(
            Adopter(
                project_id=project_id,
                full_name=first["full_name"],
                url=first["url"],
                owner=first["owner"],
                owner_avatar=first["owner_avatar"],
                tier=first["tier"],
                language=first["language"],
                profile=built or IntegrationProfile(),
            )
        )
    adopters.sort(key=lambda item: (-len(item.profile.signals), item.full_name))

    snapshots = {
        row["contract_id"]: (
            ContractSnapshot.model_validate(row["snapshot"]),
            row["observed_at"],
        )
        for row in states
    }
    used: dict[str, int] = defaultdict(int)
    for adopter in adopters:
        for contract in adopter.profile.contracts:
            used[contract.id] += 1
    contracts = [
        ContractState(
            slug=item.slug,
            id=item.id,
            name=item.name,
            network=item.network,
            kind=item.kind,
            attributes=item.attributes,
            explorer_url=_explorer(partner, item.network, item.id),
            snapshot=snapshots.get(item.id, (None, None))[0],
            observed_at=snapshots.get(item.id, (None, None))[1],
            projects=used[item.id],
            expired=_expired(snapshots.get(item.id, (None, None))[0]),
        )
        for item in profile.contracts
    ]

    signal_projects: dict[str, int] = defaultdict(int)
    check_pass: dict[str, int] = defaultdict(int)
    check_fail: dict[str, int] = defaultdict(int)
    capture_projects: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for adopter in adopters:
        for signal in adopter.profile.signals:
            signal_projects[signal.slug] += 1
        for check in adopter.profile.checks:
            (check_pass if check.status == "pass" else check_fail)[check.slug] += 1
        for name, values in adopter.profile.captures.items():
            for value in values:
                capture_projects[name][value] += 1
    offered: dict[str, list[str]] = defaultdict(list)
    lapsed: dict[str, list[str]] = defaultdict(list)
    for contract in contracts:
        if not contract.snapshot:
            continue
        base = contract.snapshot.facts.get("base")
        for item in [
            *contract.snapshot.items,
            *([base] if isinstance(base, str) else []),
        ]:
            (lapsed if item in contract.expired else offered)[item].append(
                contract.slug
            )

    return IntegrationDetail(
        slug=partner.slug,
        name=partner.name,
        category=getattr(partner, "category", "tools"),
        site=partner.site,
        networks=profile.networks,
        contracts=contracts,
        adopters=adopters,
        of_projects=total,
        signals=[
            SignalCount(
                slug=signal.slug,
                label=signal.label,
                group=signal.group,
                projects=signal_projects[signal.slug],
            )
            for signal in profile.signals
        ],
        checks=[
            CheckCount(
                slug=check.slug,
                label=check.label,
                severity=check.severity,
                passing=check_pass[check.slug],
                failing=check_fail[check.slug],
            )
            for check in profile.checks
        ],
        captures={
            name: sorted(
                (
                    CaptureCount(
                        value=value,
                        projects=count,
                        offered_by=offered.get(value, []),
                        expired_on=lapsed.get(value, []),
                    )
                    for value, count in values.items()
                ),
                key=lambda item: (-item.projects, item.value),
            )
            for name, values in capture_projects.items()
        },
        overlap=Overlap(
            total=overlap_rows[0]["total"],
            matched=sum(row["matched"] for row in overlap_rows),
            by_contract={
                next(c.slug for c in contracts if c.id == row["contract_id"]): row[
                    "matched"
                ]
                for row in overlap_rows
            },
        )
        if overlap_rows
        else None,
        live=[f"{probe.contract}:{probe.asset}" for probe in profile.live],
    )


_cache: dict[str, tuple[float, list[Reading]]] = {}


async def fetch_live(partner: Product) -> list[Reading]:
    profile = partner.profile
    assert profile
    cached = _cache.get(partner.slug)
    if cached and time.monotonic() - cached[0] < LIVE_TTL:
        return cached[1]
    if profile.adapter not in ADAPTERS:
        return []
    adapter = ADAPTERS[profile.adapter]
    async with httpx.AsyncClient(timeout=20) as http:
        readings: list[Reading] = []
        for probe in profile.live:
            contract = profile.contract(probe.contract)
            network = profile.networks[contract.network]
            reading = await adapter.probe(
                SorobanRpc(http, network.rpc_url),
                network,
                contract,
                probe.asset,
                profile.params,
            )
            if reading:
                readings.append(reading)
    _cache[partner.slug] = (time.monotonic(), readings)
    return readings


def deep_partner(slug: str) -> Product | None:
    return get_catalog().deep(slug)


def depths(uses: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for use in uses:
        grouped[use["slug"]].append((use["method"], use["evidence"]))
    found = []
    catalog = get_catalog()
    for partner in [*catalog.partners, *catalog.tools]:
        if partner.profile is None or partner.slug not in grouped:
            continue
        profile = build_profile(partner, grouped[partner.slug], NETWORK)
        if profile:
            found.append(
                {"slug": partner.slug, "name": partner.name, "profile": profile}
            )
    return found
