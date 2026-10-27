import asyncpg

from hackproof.config import get_settings

SCHEMA = """
CREATE TABLE IF NOT EXISTS contracts (
    contract_id TEXT PRIMARY KEY,
    deployer TEXT NOT NULL,
    wasm_hash TEXT NOT NULL,
    tx_hash TEXT NOT NULL,
    ledger BIGINT NOT NULL,
    deployed_at TIMESTAMPTZ NOT NULL
);
CREATE INDEX IF NOT EXISTS contracts_deployer ON contracts (deployer);
CREATE INDEX IF NOT EXISTS contracts_wasm ON contracts (wasm_hash);
CREATE INDEX IF NOT EXISTS contracts_deployed_at ON contracts (deployed_at);

CREATE TABLE IF NOT EXISTS wasm_uploads (
    tx_hash TEXT PRIMARY KEY,
    wasm_hash TEXT NOT NULL,
    uploader TEXT NOT NULL,
    size BIGINT NOT NULL,
    source_repo TEXT,
    meta JSONB NOT NULL,
    ledger BIGINT NOT NULL,
    uploaded_at TIMESTAMPTZ NOT NULL
);
CREATE INDEX IF NOT EXISTS wasm_uploads_uploader ON wasm_uploads (uploader);
CREATE INDEX IF NOT EXISTS wasm_uploads_hash ON wasm_uploads (wasm_hash);

CREATE TABLE IF NOT EXISTS failed_txs (
    tx_hash TEXT PRIMARY KEY,
    source_account TEXT NOT NULL,
    kind TEXT NOT NULL,
    result_code TEXT NOT NULL,
    ledger BIGINT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL
);
CREATE INDEX IF NOT EXISTS failed_txs_source ON failed_txs (source_account);

CREATE TABLE IF NOT EXISTS repos (
    full_name TEXT PRIMARY KEY,
    url TEXT NOT NULL,
    description TEXT,
    stars INTEGER NOT NULL DEFAULT 0,
    owner TEXT NOT NULL,
    owner_avatar TEXT,
    owner_location TEXT,
    country TEXT
);

CREATE TABLE IF NOT EXISTS wasm_repos (
    wasm_hash TEXT PRIMARY KEY,
    full_name TEXT NOT NULL,
    source TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS proofs (
    id TEXT PRIMARY KEY,
    address TEXT NOT NULL UNIQUE,
    issued_at TIMESTAMPTZ NOT NULL,
    signature TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sync_state (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""

_pool: asyncpg.Pool | None = None


async def open_pool() -> asyncpg.Pool:
    global _pool
    _pool = await asyncpg.create_pool(get_settings().database_url, min_size=1, max_size=10)
    async with _pool.acquire() as connection:
        await connection.execute(SCHEMA)
    return _pool


async def close_pool() -> None:
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None


def pool() -> asyncpg.Pool:
    if _pool is None:
        raise RuntimeError("database pool is not open")
    return _pool
