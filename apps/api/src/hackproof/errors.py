import logging
from functools import lru_cache

import asyncpg
import yaml
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from hackproof.config import get_settings
from hackproof.db import pool

log = logging.getLogger(__name__)


class Model(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class SorobanError(Model):
    code: str = Field(description="Error result code emitted by the parser or runtime")
    category: str = Field(description="Taxonomy classification category")
    plain_english: str = Field(description="Clear explanation of the error meaning")
    common_cause: str = Field(description="Typical reason why the contract or transaction failed")
    fix: str = Field(description="Actionable remediation steps to resolve the error")
    docs_url: str = Field(description="Official documentation link for deep dive")
    count: int = Field(default=0, description="Total failed transaction occurrences observed")


@lru_cache
def get_soroban_errors() -> list[SorobanError]:
    """Load curated Soroban error taxonomy from config/soroban-errors.yaml."""
    settings = get_settings()
    with settings.soroban_errors_file.open(encoding="utf-8") as f:
        data = yaml.safe_load(f) or []

    return [SorobanError.model_validate(item) for item in data]


async def get_soroban_errors_with_counts(connection: asyncpg.Connection) -> list[SorobanError]:
    """Fetch Soroban error taxonomy populated with live counts from failed_txs table."""
    errors = get_soroban_errors()
    counts_map: dict[str, int] = {}

    try:
        rows = await connection.fetch(
            "SELECT result_code, count(*)::int AS count FROM failed_txs GROUP BY result_code"
        )
        for r in rows:
            counts_map[r["result_code"]] = r["count"]
    except Exception as e:
        log.warning("Could not query failed_txs counts: %s", e)

    results: list[SorobanError] = []
    for err in errors:
        count = counts_map.get(err.code, 0)
        results.append(err.model_copy(update={"count": count}))

    results.sort(key=lambda x: (-x.count, x.code))
    return results


async def fetch_soroban_errors() -> list[SorobanError]:
    """Top-level resolver attempting db pool connection with static fallback."""
    try:
        p = pool()
        async with p.acquire() as conn:
            return await get_soroban_errors_with_counts(conn)
    except Exception as e:
        log.debug("Database pool unavailable for errors query, using base taxonomy: %s", e)
        return get_soroban_errors()
