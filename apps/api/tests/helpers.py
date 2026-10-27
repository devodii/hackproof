from datetime import timedelta

import asyncpg

from hackproof.config import get_settings
from hackproof.hackathon import get_hackathon

WINDOW = get_hackathon().window
INSIDE = WINDOW.start + timedelta(hours=3)
FRIENDBOT = get_settings().friendbot_account


async def add_repo(db: asyncpg.Connection, full_name: str, **fields: object) -> None:
    values = {"url": f"https://github.com/{full_name}", "owner": full_name.split("/")[0], **fields}
    columns = ", ".join(["full_name", *values])
    marks = ", ".join(f"${n}" for n in range(1, len(values) + 2))
    await db.execute(f"INSERT INTO repos ({columns}) VALUES ({marks})", full_name, *values.values())


async def add_ref(db: asyncpg.Connection, full_name: str, kind: str, value: str) -> None:
    await db.execute(
        "INSERT INTO repo_refs VALUES ($1, $2, $3, 'README.md')", full_name, kind, value
    )


async def add_contract(db: asyncpg.Connection, contract: str, deployer: str, wasm: str) -> None:
    await db.execute(
        "INSERT INTO contracts VALUES ($1, $2, $3, $4, 1, $5)",
        contract, deployer, wasm, f"tx-{contract}", INSIDE,
    )  # fmt: skip


async def add_upload(db: asyncpg.Connection, wasm: str, uploader: str, repo: str | None = None):
    await db.execute(
        "INSERT INTO wasm_uploads VALUES ($1, $2, $3, 10, $4, '{}', 1, $5)",
        f"up-{wasm}-{uploader}", wasm, uploader, repo, INSIDE,
    )  # fmt: skip


async def add_funding(db: asyncpg.Connection, account: str) -> None:
    await db.execute(
        "INSERT INTO accounts VALUES ($1, $2, $3, 1, $4)",
        account,
        FRIENDBOT,
        f"fund-{account}",
        INSIDE,
    )


async def links(db: asyncpg.Connection) -> dict[tuple[str, str, str], str]:
    rows = await db.fetch("SELECT full_name, subject_kind, subject, method FROM links")
    return {(r["full_name"], r["subject_kind"], r["subject"]): r["method"] for r in rows}


STELLAR = {"ecosystems": ["js"], "packages": {"@stellar/stellar-sdk": "14.0.0"}}


async def tiers(db: asyncpg.Connection) -> dict[str, str]:
    rows = await db.fetch("SELECT project_id, tier FROM projects")
    return {row["project_id"]: row["tier"] for row in rows}
