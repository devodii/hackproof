import asyncio
import logging
from pathlib import Path
import sys

import asyncpg

# Add apps/api/src to sys.path so we can import hackproof config and schema
REPO_ROOT = Path(__file__).resolve().parents[1]
API_SRC = REPO_ROOT / "apps" / "api" / "src"
if str(API_SRC) not in sys.path:
    sys.path.insert(0, str(API_SRC))

from hackproof.config import get_settings
from hackproof.db import SCHEMA

log = logging.getLogger("hackproof.seed")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

SAMPLE_SQL_PATH = REPO_ROOT / "data" / "sample" / "sample.sql"


async def load_sample() -> None:
    settings = get_settings()
    log.info("Connecting to database at %s...", settings.database_url)

    # Retry connection for docker compose startup grace period
    conn = None
    for attempt in range(1, 15):
        try:
            conn = await asyncpg.connect(settings.database_url)
            break
        except Exception as e:
            log.warning("Database connection attempt %d/15 failed (%s). Retrying in 2s...", attempt, e)
            await asyncio.sleep(2)

    if conn is None:
        log.error("Could not connect to database after 15 attempts.")
        sys.exit(1)

    try:
        # Initialize schema if not present
        await conn.execute(SCHEMA)

        # Check if projects table already contains data
        count: int = await conn.fetchval("SELECT count(*) FROM projects")
        if count > 0:
            log.info("Projects table already contains %d projects. Skipping sample seed.", count)
            return

        if not SAMPLE_SQL_PATH.exists():
            log.error("Sample SQL file not found at %s", SAMPLE_SQL_PATH)
            sys.exit(1)

        sql_content = SAMPLE_SQL_PATH.read_text(encoding="utf-8")
        await conn.execute(sql_content)

        new_count: int = await conn.fetchval("SELECT count(*) FROM projects")
        contract_count: int = await conn.fetchval("SELECT count(*) FROM contracts")
        log.info(
            "Successfully seeded sample database: %d projects, %d contracts loaded.",
            new_count,
            contract_count,
        )
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(load_sample())
