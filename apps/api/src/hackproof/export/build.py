from collections import defaultdict
from collections.abc import Iterable
from typing import Any

import asyncpg

from hackproof.export.models import (
    Account,
    AgentEvidence,
    AiAgent,
    Chain,
    Contract,
    Contributor,
    EcosystemTool,
    Evidence,
    Hackathon as ExportedHackathon,
    HackathonExport,
    IntegrationEvidence,
    IntegrationPartner,
    Owner,
    Project,
    WasmUpload,
)
from hackproof.export.urls import (
    account_url,
    asset_url,
    contract_url,
    repo_file_url,
    tx_url,
)
from hackproof.hackathon import Hackathon
from hackproof.integrations.catalog import Catalog, get_catalog
from hackproof.integrations.profile import build_profile
from hackproof.sql_loader import load_sql

EVENT_NETWORK = "testnet"
STRICT_TIERS = ("verified", "likely")
TIER_ORDER = ("verified", "likely", "possible")


def _evidence_url(kind: str, subject: str) -> str | None:
    match kind:
        case "contract":
            return contract_url(subject)
        case "account":
            return account_url(subject)
        case "asset":
            return asset_url(subject)
        case _:
            return None


def _group(
    rows: Iterable[asyncpg.Record], key: str = "full_name"
) -> dict[str, list[Any]]:
    grouped: dict[str, list[Any]] = defaultdict(list)
    for row in rows:
        grouped[row[key]].append(row)
    return grouped


def _found(
    rows: list[asyncpg.Record], key: str, repo_url: str
) -> dict[str, list[IntegrationEvidence]]:
    found: dict[str, list[IntegrationEvidence]] = defaultdict(list)
    for row in rows:
        found[row[key]].append(
            IntegrationEvidence(
                method=row["method"],
                detail=row["evidence"],
                repo_file_url=repo_file_url(repo_url, row["path"]),
            )
        )
    return found


def _agents(
    catalog: Catalog, rows: list[asyncpg.Record], repo_url: str
) -> list[AiAgent]:
    found: dict[str, list[AgentEvidence]] = defaultdict(list)
    for row in rows:
        found[row["agent"]].append(
            AgentEvidence(
                method=row["method"],
                detail=row["evidence"],
                repo_file_url=repo_file_url(repo_url, row["path"])
                if row["path"]
                else None,
            )
        )
    return [
        AiAgent(
            slug=agent.slug,
            name=agent.name,
            website=agent.site,
            evidence=found[agent.slug],
        )
        for agent in catalog.agents
        if agent.slug in found
    ]


def _tools(
    catalog: Catalog, rows: list[asyncpg.Record], repo_url: str
) -> list[EcosystemTool]:
    found = _found(rows, "tool", repo_url)
    raw = defaultdict(list)
    for row in rows:
        raw[row["tool"]].append((row["method"], row["evidence"]))
    return [
        EcosystemTool(
            slug=tool.slug,
            name=tool.name,
            website=tool.site,
            evidence=found[tool.slug],
            profile=build_profile(tool, raw[tool.slug], EVENT_NETWORK),
        )
        for tool in catalog.tools
        if tool.slug in found
    ]


def _partners(
    catalog: Catalog, rows: list[asyncpg.Record], repo_url: str
) -> list[IntegrationPartner]:
    found = _found(rows, "partner", repo_url)
    raw = defaultdict(list)
    for row in rows:
        raw[row["partner"]].append((row["method"], row["evidence"]))
    return [
        IntegrationPartner(
            slug=partner.slug,
            name=partner.name,
            category=partner.category,
            website=partner.site,
            evidence=found[partner.slug],
            profile=build_profile(partner, raw[partner.slug], EVENT_NETWORK),
        )
        for partner in catalog.partners
        if partner.slug in found
    ]


async def build_export(
    connection: asyncpg.Connection,
    hackathon: Hackathon,
    tiers: Iterable[str] = STRICT_TIERS,
) -> HackathonExport:
    window = hackathon.window
    projects = await connection.fetch(
        load_sql("export/projects"), list(tiers), list(TIER_ORDER)
    )
    names = [row["full_name"] for row in projects]
    span = (window.start, window.end)

    contributors = _group(
        await connection.fetch(load_sql("export/contributors"), names)
    )
    contracts = _group(
        await connection.fetch(load_sql("export/contracts"), names, *span)
    )
    accounts = _group(await connection.fetch(load_sql("export/accounts"), names))
    wasm = _group(await connection.fetch(load_sql("export/wasm"), names, *span))
    evidence = _group(await connection.fetch(load_sql("export/evidence"), names))
    integrations = _group(
        await connection.fetch(load_sql("export/integrations"), names)
    )
    tools = _group(await connection.fetch(load_sql("export/tools"), names))
    agents = _group(await connection.fetch(load_sql("export/agents"), names))
    catalog = get_catalog()
    awards = {award.project_id: award.place for award in hackathon.awards}

    exported = [
        Project(
            repo_full_name=row["full_name"],
            repo_url=row["url"],
            name=row["full_name"].split("/")[1],
            description=row["description"],
            homepage=row["homepage"],
            tier=row["tier"],
            award=awards.get(f"repo:{row['full_name']}"),
            language=row["language"],
            license=row["license"],
            stars=row["stars"],
            forks=row["forks"],
            self_tags=row["topics"],
            stack=list(row["dependencies"].get("packages", {})),
            stack_versions=row["dependencies"].get("packages", {}),
            repo_created_at=row["created_at"],
            repo_last_commit_at=row["pushed_at"],
            commits_in_window=row["window_commits"],
            total_commits=row["total_commits"],
            track=row["declared_track"] or "genesis",
            track_declared=row["declared_track"] is not None,
            integration_partners=_partners(
                catalog, integrations[row["full_name"]], row["url"]
            ),
            ecosystem_tools=_tools(catalog, tools[row["full_name"]], row["url"]),
            ai_agents=_agents(catalog, agents[row["full_name"]], row["url"]),
            owner=Owner(
                login=row["owner"],
                avatar_url=row["owner_avatar"],
                country=row["country"],
            ),
            contributors=[
                Contributor(
                    login=c["login"],
                    url=c["url"],
                    avatar_url=c["avatar_url"],
                    contributions=c["contributions"],
                    country=c["country"],
                )
                for c in contributors[row["full_name"]]
            ],
            chain=Chain(
                contract_count=row["contracts"],
                wasm_upload_count=row["wasm_uploads"],
                classic_op_count=row["classic_ops"],
                asset_count=row["assets"],
                failed_tx_count=row["failed_txs"],
                accounts=[
                    Account(
                        address=a["subject"], explorer_url=account_url(a["subject"])
                    )
                    for a in accounts[row["full_name"]]
                ],
                wasm_uploads=[
                    WasmUpload(
                        wasm_hash=w["wasm_hash"],
                        upload_tx=w["tx_hash"],
                        explorer_url=tx_url(w["tx_hash"]),
                    )
                    for w in wasm[row["full_name"]]
                ],
                contracts=[
                    Contract(
                        contract_id=c["contract_id"],
                        deployer=c["deployer"],
                        wasm_hash=c["wasm_hash"],
                        deployed_at=c["deployed_at"],
                        ledger=c["ledger"],
                        tx_hash=c["tx_hash"],
                        explorer_url=contract_url(c["contract_id"]),
                        tx_url=tx_url(c["tx_hash"]),
                    )
                    for c in contracts[row["full_name"]]
                ],
                evidence=[
                    Evidence(
                        kind=e["subject_kind"],
                        subject=e["subject"],
                        method=e["method"],
                        explorer_url=_evidence_url(e["subject_kind"], e["subject"]),
                        repo_file_url=(
                            repo_file_url(row["url"], e["path"]) if e["path"] else None
                        ),
                    )
                    for e in evidence[row["full_name"]]
                ],
            ),
        )
        for row in projects
    ]
    return HackathonExport(
        hackathon=ExportedHackathon(
            slug=hackathon.slug,
            name=hackathon.name,
            network=EVENT_NETWORK,
            starts_at=window.start,
            submission_deadline=window.end,
        ),
        projects=exported,
    )
