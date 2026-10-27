from datetime import datetime
from typing import Any

from hackproof import queries
from hackproof.config import get_settings
from hackproof.db import pool
from hackproof.proof import proof_id

ACTIVITY_SQL = """
SELECT
    (SELECT count(*) FROM contracts WHERE deployer = $1 AND deployed_at BETWEEN $2 AND $3)
        AS contracts,
    (SELECT count(*) FROM wasm_uploads WHERE uploader = $1 AND uploaded_at BETWEEN $2 AND $3)
        AS wasm_uploads,
    (SELECT count(*) FROM failed_txs WHERE source_account = $1 AND created_at BETWEEN $2 AND $3)
        AS failed_txs,
    (SELECT min(at) FROM (
        SELECT deployed_at AS at FROM contracts WHERE deployer = $1
        UNION ALL SELECT uploaded_at FROM wasm_uploads WHERE uploader = $1
        UNION ALL SELECT created_at FROM failed_txs WHERE source_account = $1
    ) a WHERE at BETWEEN $2 AND $3) AS first_activity,
    (SELECT max(at) FROM (
        SELECT deployed_at AS at FROM contracts WHERE deployer = $1
        UNION ALL SELECT uploaded_at FROM wasm_uploads WHERE uploader = $1
        UNION ALL SELECT created_at FROM failed_txs WHERE source_account = $1
    ) a WHERE at BETWEEN $2 AND $3) AS last_activity
"""


async def activity(address: str) -> dict[str, Any] | None:
    start, end = queries.window()
    async with pool().acquire() as connection:
        row = await connection.fetchrow(ACTIVITY_SQL, address, start, end)
    if row["first_activity"] is None:
        return None
    _, projects = await queries.list_page("projects", account=address, limit=1)
    return {**dict(row), "projects": projects}


async def store_claim(address: str, signature: str, claimed_at: datetime) -> None:
    async with pool().acquire() as connection:
        await connection.execute(
            "INSERT INTO proofs VALUES ($1, $2, $3, $4) ON CONFLICT (address) DO NOTHING",
            proof_id(address),
            address,
            claimed_at,
            signature,
        )


async def load_proof(address: str) -> dict[str, Any] | None:
    async with pool().acquire() as connection:
        claimed = await connection.fetchrow(
            "SELECT issued_at FROM proofs WHERE address = $1", address
        )
    if claimed is None:
        return None
    found = await activity(address)
    if found is None:
        return None
    settings = get_settings()
    return {
        **found,
        "proof_id": proof_id(address),
        "address": address,
        "claimed_at": claimed["issued_at"],
        "window_start": settings.hack_start,
        "window_end": settings.hack_end,
    }
