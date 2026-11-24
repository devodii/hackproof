import asyncpg
from trawl.db.pool import open_pool as connect

from hackproof.config import get_settings

_pool: asyncpg.Pool | None = None


async def open_pool() -> asyncpg.Pool:
    global _pool
    _pool = await connect(get_settings().database_url)
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
