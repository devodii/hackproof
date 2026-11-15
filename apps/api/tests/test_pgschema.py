import sys
from pathlib import Path

import pytest

from hackproof.db_utils import pgschema
from hackproof.db_utils.connection import Connection
from hackproof.db_utils.guard import destructive_statements
from hackproof.db_utils.manifest import manifest_text, order_by_dependency
from hackproof.linking.methods import LinkMethod

NEON = "postgresql://owner:p%40ss@ep-cool-1234.us-east-2.aws.neon.tech/hackproof?sslmode=require&channel_binding=require"


def write(root: Path, files: dict[str, str]) -> Path:
    for name, text in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    return root


def test_a_connection_is_read_from_a_url():
    connection = Connection.from_url(NEON)

    assert connection.host == "ep-cool-1234.us-east-2.aws.neon.tech"
    assert connection.port == 5432
    assert connection.user == "owner"
    assert connection.password == "p@ss"
    assert connection.database == "hackproof"
    assert connection.sslmode == "require"
    assert not connection.is_local


def test_a_local_database_is_reached_through_the_host_the_container_can_see(
    monkeypatch,
):
    local = Connection.from_url("postgresql://u:p@localhost:5440/hackproof")

    monkeypatch.setattr(sys, "platform", "darwin")
    assert local.container_route() == (
        ["--add-host", "host.docker.internal:host-gateway"],
        "host.docker.internal",
    )
    monkeypatch.setattr(sys, "platform", "linux")
    assert local.container_route() == (["--network", "host"], "localhost")
    assert Connection.from_url(NEON).container_route() == (
        [],
        "ep-cool-1234.us-east-2.aws.neon.tech",
    )


def test_the_password_never_appears_in_the_docker_command(tmp_path):
    connection = Connection.from_url(NEON)

    command = pgschema.docker_command(
        "plan",
        "--file",
        "/db/schema/manifest.sql",
        connection=connection,
        mounts={tmp_path: "/db"},
        image="pgplex/pgschema:1.14.1",
    )

    assert not any("p@ss" in part or "p%40ss" in part for part in command)
    assert command[command.index("-e") + 1] == "PGPASSWORD"
    assert command[command.index("--sslmode") + 1] == "require"
    assert f"{tmp_path}:/db" in command


@pytest.mark.parametrize(
    "sql",
    [
        "DROP TABLE IF EXISTS wasm_repos CASCADE;",
        "ALTER TABLE repos DROP COLUMN stars;",
        "ALTER TABLE repos ALTER COLUMN stars TYPE bigint;",
        "alter table repos drop column stars;",
        "TRUNCATE contracts;",
        "DELETE FROM projects;",
    ],
)
def test_the_guard_flags_statements_that_can_lose_data(sql):
    assert destructive_statements(sql)


def test_the_guard_lets_additive_and_data_safe_changes_through():
    sql = """
    CREATE TABLE notes (id text PRIMARY KEY);
    ALTER TABLE repos ADD COLUMN notes text;
    CREATE INDEX notes_id ON notes (id);
    DROP INDEX IF EXISTS contracts_wasm;
    DROP VIEW IF EXISTS attribution;
    DROP FUNCTION IF EXISTS method_rank(text);
    ALTER TABLE repos DROP CONSTRAINT repos_pkey;
    -- DROP TABLE contracts;
    """

    assert destructive_statements(sql) == []


def test_tables_load_after_the_tables_they_reference(tmp_path):
    root = write(
        tmp_path,
        {
            "a_child.sql": "CREATE TABLE a_child (p text REFERENCES z_parent (id));",
            "z_parent.sql": "CREATE TABLE z_parent (id text PRIMARY KEY);",
        },
    )

    assert [f.name for f in order_by_dependency("tables", root)] == [
        "z_parent.sql",
        "a_child.sql",
    ]


def test_views_load_after_the_views_they_select_from(tmp_path):
    root = write(
        tmp_path,
        {
            "account_projects.sql": "CREATE OR REPLACE VIEW account_projects AS SELECT 1 FROM attribution;",
            "attribution.sql": "CREATE OR REPLACE VIEW attribution AS SELECT 1 FROM links;",
        },
    )

    assert [f.name for f in order_by_dependency("views", root)] == [
        "attribution.sql",
        "account_projects.sql",
    ]


def test_the_committed_manifest_matches_the_schema_files():
    committed = (pgschema.SCHEMA_DIR / "manifest.sql").read_text()

    assert committed == manifest_text(pgschema.SCHEMA_DIR)


def test_migrations_are_numbered_one_after_another(tmp_path, monkeypatch):
    monkeypatch.setattr(pgschema, "MIGRATIONS_DIR", tmp_path)
    assert pgschema.next_migration_path().name == "000001.sql"

    write(tmp_path, {"000001.sql": "x", "000002.sql": "y", "notes.md": "z"})
    assert pgschema.next_migration_path().name == "000003.sql"


async def test_the_sql_method_rank_follows_the_python_order(scratch_db):
    for position, method in enumerate(LinkMethod, start=1):
        assert await scratch_db.fetchval("SELECT method_rank($1)", method) == position
    assert await scratch_db.fetchval("SELECT method_rank('unknown')") is None
