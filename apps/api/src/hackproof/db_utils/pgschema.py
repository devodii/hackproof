from pathlib import Path

from trawl.schema import pgschema as schema
from trawl.schema.connection import Connection

from hackproof.config import ROOT, get_settings

API_DIR = ROOT / "apps" / "api"
DB_DIR = API_DIR / "db"
SCHEMA_DIR = DB_DIR / "schema"
MIGRATIONS_DIR = DB_DIR / "migrations"
TARGET = schema.Target(
    name="hackproof", db_dir=DB_DIR, image=get_settings().pgschema_image
)


def plan(connection: Connection, *, format: bool = True) -> int:
    return schema.plan(connection, format=format, target=TARGET)


def apply(
    connection: Connection,
    *,
    allow_destructive: bool = False,
    out_dir: Path | None = None,
) -> int:
    return schema.apply(
        connection,
        allow_destructive=allow_destructive,
        out_dir=out_dir,
        target=TARGET,
    )


def verify(connection: Connection) -> int:
    return schema.verify(connection, TARGET)
