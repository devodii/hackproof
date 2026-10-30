from collections import defaultdict
from collections.abc import Iterable
from datetime import UTC, datetime
from typing import Any

import asyncpg

from hackproof.export.models import (
    SCHEMA_VERSION,
    Account,
    Chain,
    Contract,
    Contributor,
    Evidence,
    HackathonExport,
    IntegrationEvidence,
    IntegrationPartner,
    Owner,
    Project,
    WasmUpload,
)
from hackproof.export.models import Hackathon as ExportedHackathon
from hackproof.export.urls import (
    account_url,
    asset_url,
    contract_url,
    repo_file_url,
    tx_url,
)
from hackproof.hackathon import Hackathon
from hackproof.integrations.catalog import Catalog, get_catalog
from hackproof.linking.methods import METHOD_RANK_SQL

STRICT_TIERS = ("verified", "likely")
TIER_ORDER = ("verified", "likely", "possible")

PROJECTS_SQL = """
SELECT p.full_name, p.tier, p.contracts, p.classic_ops, p.assets, p.wasm_uploads, p.failed_txs,
       r.url, r.description, r.homepage, r.language, r.license, r.stars, r.forks, r.topics,
       r.dependencies, r.created_at, r.pushed_at, r.window_commits, r.total_commits,
       r.owner, r.owner_avatar, r.country, r.declared_track
FROM projects p
JOIN repos r ON r.full_name = p.full_name
WHERE p.tier = ANY($1)
ORDER BY array_position($2::text[], p.tier), p.contracts DESC, r.stars DESC, p.full_name
"""

CONTRIBUTORS_SQL = """
SELECT c.full_name, c.login, c.url, c.avatar_url, c.contributions, u.country
FROM repo_contributors c
LEFT JOIN github_users u ON u.login = c.login
WHERE c.full_name = ANY($1)
ORDER BY c.contributions DESC, c.login
"""

CONTRACTS_SQL = """
SELECT a.full_name, c.contract_id, c.deployer, c.wasm_hash, c.deployed_at, c.ledger, c.tx_hash
FROM contracts c
JOIN attribution a ON a.subject_kind = 'contract' AND a.subject = c.contract_id
WHERE a.full_name = ANY($1) AND c.deployed_at BETWEEN $2 AND $3
ORDER BY c.deployed_at
"""

ACCOUNTS_SQL = """
SELECT full_name, subject FROM links
WHERE subject_kind = 'account' AND full_name = ANY($1)
ORDER BY subject
"""

WASM_SQL = """
SELECT DISTINCT ON (a.full_name, w.wasm_hash) a.full_name, w.wasm_hash, w.tx_hash
FROM wasm_uploads w
JOIN attribution a ON a.subject_kind = 'account' AND a.subject = w.uploader
WHERE a.full_name = ANY($1) AND w.uploaded_at BETWEEN $2 AND $3
ORDER BY a.full_name, w.wasm_hash, w.uploaded_at
"""

EVIDENCE_SQL = f"""
SELECT l.full_name, l.subject_kind, l.subject, l.method, r.path
FROM links l
LEFT JOIN repo_refs r
       ON r.full_name = l.full_name AND r.kind = l.subject_kind AND r.value = l.subject
WHERE l.full_name = ANY($1) AND l.method <> 'footprint'
ORDER BY {METHOD_RANK_SQL}, l.subject_kind, l.subject
"""

INTEGRATIONS_SQL = """
SELECT full_name, partner, method, evidence, path
FROM repo_integrations
WHERE full_name = ANY($1)
ORDER BY partner, method, evidence
"""


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


def _group(rows: Iterable[asyncpg.Record], key: str = "full_name") -> dict[str, list[Any]]:
    grouped: dict[str, list[Any]] = defaultdict(list)
    for row in rows:
        grouped[row[key]].append(row)
    return grouped


def _partners(
    catalog: Catalog, rows: list[asyncpg.Record], repo_url: str
) -> list[IntegrationPartner]:
    found: dict[str, list[IntegrationEvidence]] = defaultdict(list)
    for row in rows:
        found[row["partner"]].append(
            IntegrationEvidence(
                method=row["method"],
                detail=row["evidence"],
                repo_file_url=repo_file_url(repo_url, row["path"]),
            )
        )
    return [
        IntegrationPartner(
            slug=partner.slug,
            name=partner.name,
            category=partner.category,
            website=partner.site,
            evidence=found[partner.slug],
        )
        for partner in catalog.partners
        if partner.slug in found
    ]


async def build_export(
    connection: asyncpg.Connection, hackathon: Hackathon, tiers: Iterable[str] = STRICT_TIERS
) -> HackathonExport:
    window = hackathon.window
    projects = await connection.fetch(PROJECTS_SQL, list(tiers), list(TIER_ORDER))
    names = [row["full_name"] for row in projects]
    span = (window.start, window.end)

    contributors = _group(await connection.fetch(CONTRIBUTORS_SQL, names))
    contracts = _group(await connection.fetch(CONTRACTS_SQL, names, *span))
    accounts = _group(await connection.fetch(ACCOUNTS_SQL, names))
    wasm = _group(await connection.fetch(WASM_SQL, names, *span))
    evidence = _group(await connection.fetch(EVIDENCE_SQL, names))
    integrations = _group(await connection.fetch(INTEGRATIONS_SQL, names))
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
            track=row["declared_track"],
            integration_partners=_partners(catalog, integrations[row["full_name"]], row["url"]),
            owner=Owner(login=row["owner"], avatar_url=row["owner_avatar"], country=row["country"]),
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
                    Account(address=a["subject"], explorer_url=account_url(a["subject"]))
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
                        repo_file_url=(repo_file_url(row["url"], e["path"]) if e["path"] else None),
                    )
                    for e in evidence[row["full_name"]]
                ],
            ),
        )
        for row in projects
    ]
    return HackathonExport(
        schema_version=SCHEMA_VERSION,
        generated_at=datetime.now(UTC),
        hackathon=ExportedHackathon(
            slug=hackathon.slug,
            name=hackathon.name,
            network="testnet",
            starts_at=window.start,
            submission_deadline=window.end,
        ),
        projects=exported,
    )
