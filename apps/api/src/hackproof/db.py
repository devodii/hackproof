import json

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

CREATE TABLE IF NOT EXISTS accounts (
    account TEXT PRIMARY KEY,
    funder TEXT NOT NULL,
    tx_hash TEXT NOT NULL,
    ledger BIGINT NOT NULL,
    funded_at TIMESTAMPTZ NOT NULL
);
CREATE INDEX IF NOT EXISTS accounts_funder ON accounts (funder);

CREATE TABLE IF NOT EXISTS classic_ops (
    tx_hash TEXT NOT NULL,
    op_index INTEGER NOT NULL,
    source_account TEXT NOT NULL,
    op_type TEXT NOT NULL,
    asset TEXT,
    counterparty TEXT,
    ledger BIGINT NOT NULL,
    occurred_at TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (tx_hash, op_index)
);
CREATE INDEX IF NOT EXISTS classic_ops_source ON classic_ops (source_account);
CREATE INDEX IF NOT EXISTS classic_ops_asset ON classic_ops (asset) WHERE asset IS NOT NULL;

CREATE TABLE IF NOT EXISTS repos (
    full_name TEXT PRIMARY KEY,
    url TEXT NOT NULL,
    description TEXT,
    stars INTEGER NOT NULL DEFAULT 0,
    owner TEXT NOT NULL,
    owner_avatar TEXT,
    owner_location TEXT,
    country TEXT,
    default_branch TEXT,
    homepage TEXT,
    language TEXT,
    license TEXT,
    forks INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ,
    pushed_at TIMESTAMPTZ,
    topics TEXT[] NOT NULL DEFAULT '{}',
    discovered_via TEXT[] NOT NULL DEFAULT '{}',
    dependencies JSONB NOT NULL DEFAULT '{}',
    window_commits INTEGER,
    base_sha TEXT,
    total_commits INTEGER,
    mentions_hackathon BOOLEAN NOT NULL DEFAULT FALSE,
    stellar_added_in_window BOOLEAN,
    scanned_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS repo_contributors (
    full_name TEXT NOT NULL,
    login TEXT NOT NULL,
    url TEXT NOT NULL,
    avatar_url TEXT,
    contributions INTEGER NOT NULL,
    PRIMARY KEY (full_name, login)
);
CREATE INDEX IF NOT EXISTS repo_contributors_login ON repo_contributors (login);

CREATE TABLE IF NOT EXISTS github_users (
    login TEXT PRIMARY KEY,
    location TEXT,
    country TEXT,
    fetched_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS repo_refs (
    full_name TEXT NOT NULL,
    kind TEXT NOT NULL,
    value TEXT NOT NULL,
    path TEXT NOT NULL,
    PRIMARY KEY (full_name, kind, value)
);
CREATE INDEX IF NOT EXISTS repo_refs_value ON repo_refs (kind, value);

CREATE TABLE IF NOT EXISTS links (
    full_name TEXT NOT NULL,
    subject_kind TEXT NOT NULL,
    subject TEXT NOT NULL,
    method TEXT NOT NULL,
    confidence REAL NOT NULL,
    PRIMARY KEY (subject_kind, subject, full_name)
);

CREATE TABLE IF NOT EXISTS projects (
    project_id TEXT PRIMARY KEY,
    full_name TEXT,
    footprint TEXT NOT NULL,
    contracts INTEGER NOT NULL,
    classic_ops INTEGER NOT NULL,
    assets INTEGER NOT NULL,
    wasm_uploads INTEGER NOT NULL,
    failed_txs INTEGER NOT NULL,
    builders INTEGER NOT NULL,
    first_activity TIMESTAMPTZ,
    last_activity TIMESTAMPTZ,
    linked BOOLEAN NOT NULL
);

CREATE OR REPLACE VIEW attribution AS
SELECT DISTINCT ON (subject_kind, subject) subject_kind, subject, full_name, method, confidence
FROM links
ORDER BY subject_kind, subject, confidence DESC, method;

CREATE OR REPLACE VIEW account_projects AS
SELECT subject AS account, 'repo:' || full_name AS project_id
FROM attribution WHERE subject_kind = 'account';

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


async def _init_connection(connection: asyncpg.Connection) -> None:
    await connection.set_type_codec(
        "jsonb", encoder=json.dumps, decoder=json.loads, schema="pg_catalog"
    )


async def open_pool() -> asyncpg.Pool:
    global _pool
    _pool = await asyncpg.create_pool(
        get_settings().database_url, min_size=1, max_size=10, init=_init_connection
    )
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
