from collections import defaultdict
from collections.abc import Iterable
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from hackproof.integrations.catalog import Partner


class Model(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ProfileContractUse(Model):
    slug: str = Field(description="Stable contract id in data/integrations.yaml")
    id: str = Field(description="Contract address found in the repo")
    name: str = Field(description="What the contract is, for example Fiat FX")
    network: str = Field(description="Network the contract lives on")
    kind: str = Field(description="feed or token")
    explorer_url: str = Field(description="Stellar Expert page for the contract")
    attributes: dict[str, str] = Field(
        default_factory=dict, description="Extra facts the catalog records"
    )


class ProfileSignal(Model):
    slug: str = Field(description="Stable signal id in data/integrations.yaml")
    group: str = Field(
        description="How the catalog groups the signal, for example client, read, safety or risk"
    )
    label: str = Field(description="What the signal means")


class ProfileCheck(Model):
    slug: str = Field(description="Stable check id in data/integrations.yaml")
    label: str = Field(description="What the check looks for")
    status: Literal["pass", "warn", "fail"] = Field(
        description="pass: the guard is there. warn or fail: the catalog's severity when it is missing"
    )


class IntegrationProfile(Model):
    contracts: list[ProfileContractUse] = Field(
        default_factory=list,
        description="Known contracts of the partner that the repo references",
    )
    signals: list[ProfileSignal] = Field(
        default_factory=list,
        description="How the code uses the partner, matched in source files",
    )
    captures: dict[str, list[str]] = Field(
        default_factory=dict,
        description="Values pulled out of source, for example the assets requested from an oracle",
    )
    checks: list[ProfileCheck] = Field(
        default_factory=list,
        description="The partner's own integration checklist applied to the repo",
    )


def build_profile(
    partner: Partner, evidence: Iterable[tuple[str, str]], network: str
) -> IntegrationProfile | None:
    profile = partner.profile
    if profile is None:
        return None
    by_id = {contract.id: contract for contract in profile.contracts}
    signals = {signal.slug: signal for signal in profile.signals}
    found_signals: set[str] = set()
    found_contracts: list[str] = []
    captures: dict[str, list[str]] = defaultdict(list)
    for method, detail in evidence:
        if method == "contract" and detail in by_id:
            found_contracts.append(detail)
        elif method == "signal" and detail in signals:
            found_signals.add(detail)
        elif method == "capture":
            name, _, value = detail.partition(":")
            captures[name].append(value)
    explorers = {slug: item.explorer for slug, item in profile.networks.items()}
    contracts = [
        ProfileContractUse(
            slug=by_id[contract_id].slug,
            id=contract_id,
            name=by_id[contract_id].name,
            network=by_id[contract_id].network,
            kind=by_id[contract_id].kind,
            explorer_url=f"{explorers[by_id[contract_id].network]}/{contract_id}",
            attributes=by_id[contract_id].attributes,
        )
        for contract_id in sorted(found_contracts)
    ]
    checks: list[ProfileCheck] = []
    feed_networks = {item.network for item in contracts if item.kind == "feed"}
    for check in profile.checks:
        if check.only_networks:
            if feed_networks and feed_networks <= set(check.only_networks):
                if network not in check.only_networks:
                    checks.append(
                        ProfileCheck(
                            slug=check.slug, label=check.label, status=check.severity
                        )
                    )
            continue
        if not set(check.requires) <= found_signals:
            continue
        broken = not any(slug in found_signals for slug in check.missing)
        checks.append(
            ProfileCheck(
                slug=check.slug,
                label=check.label,
                status=check.severity if broken else "pass",
            )
        )
    return IntegrationProfile(
        contracts=contracts,
        signals=[
            signals[slug]
            and ProfileSignal(
                slug=slug, group=signals[slug].group, label=signals[slug].label
            )
            for slug in signals
            if slug in found_signals
        ],
        captures={name: sorted(set(values)) for name, values in captures.items()},
        checks=checks,
    )
