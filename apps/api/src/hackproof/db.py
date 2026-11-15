import json

import asyncpg

from hackproof.config import get_settings

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
