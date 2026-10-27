from collections.abc import AsyncIterator
from urllib.parse import urlparse, urlunparse
from uuid import uuid4

import asyncpg
import pytest

from hackproof.config import get_settings
from hackproof.db import SCHEMA


@pytest.fixture
async def scratch_db() -> AsyncIterator[asyncpg.Connection]:
    url = get_settings().database_url
    name = f"hackproof_test_{uuid4().hex[:8]}"
    admin = await asyncpg.connect(url)
    await admin.execute(f'CREATE DATABASE "{name}"')
    connection = await asyncpg.connect(urlunparse(urlparse(url)._replace(path=f"/{name}")))
    await connection.execute(SCHEMA)
    yield connection
    await connection.close()
    await admin.execute(f'DROP DATABASE "{name}"')
    await admin.close()
