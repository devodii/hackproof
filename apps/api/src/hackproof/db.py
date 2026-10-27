from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import aiosqlite

from hackproof.config import get_settings

SCHEMA = """
CREATE TABLE IF NOT EXISTS contracts (
    contract_id TEXT PRIMARY KEY,
    deployer TEXT NOT NULL,
    wasm_hash TEXT,
    tx_hash TEXT NOT NULL,
    ledger INTEGER NOT NULL,
    deployed_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS contracts_deployer ON contracts (deployer);
CREATE INDEX IF NOT EXISTS contracts_wasm ON contracts (wasm_hash);

CREATE TABLE IF NOT EXISTS wasm_uploads (
    wasm_hash TEXT NOT NULL,
    uploader TEXT NOT NULL,
    tx_hash TEXT PRIMARY KEY,
    ledger INTEGER NOT NULL,
    uploaded_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS wasm_uploads_uploader ON wasm_uploads (uploader);

CREATE TABLE IF NOT EXISTS failed_txs (
    tx_hash TEXT PRIMARY KEY,
    source_account TEXT NOT NULL,
    result_code TEXT NOT NULL,
    ledger INTEGER NOT NULL,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS failed_txs_source ON failed_txs (source_account);

CREATE TABLE IF NOT EXISTS repos (
    wasm_hash TEXT PRIMARY KEY,
    repo_url TEXT NOT NULL,
    source TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sync_state (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""


async def init_db() -> None:
    async with aiosqlite.connect(get_settings().database_path) as db:
        await db.executescript(SCHEMA)
        await db.commit()


@asynccontextmanager
async def connect() -> AsyncIterator[aiosqlite.Connection]:
    async with aiosqlite.connect(get_settings().database_path) as db:
        db.row_factory = aiosqlite.Row
        yield db
