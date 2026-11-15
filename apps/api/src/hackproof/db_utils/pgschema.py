import os
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

from hackproof.config import ROOT, get_settings
from hackproof.db_utils.connection import Connection
from hackproof.db_utils.guard import destructive_statements
from hackproof.db_utils.manifest import generate_manifest, manifest_text

API_DIR = ROOT / "apps" / "api"
DB_DIR = API_DIR / "db"
SCHEMA_DIR = DB_DIR / "schema"
MIGRATIONS_DIR = DB_DIR / "migrations"
MANIFEST = "/db/schema/manifest.sql"
LOCK_TIMEOUT = "30s"


def docker_command(
    command: str,
    *args: str,
    connection: Connection,
    mounts: dict[Path, str],
    image: str,
) -> list[str]:
    network, host = connection.container_route()
    mount_flags = [
        flag
        for source, target in mounts.items()
        for flag in ("-v", f"{source}:{target}")
    ]
    return [
        "docker",
        "run",
        "--rm",
        "-i",
        *network,
        "-e",
        "PGPASSWORD",
        *mount_flags,
        image,
        command,
        "--host",
        host,
        "--port",
        str(connection.port),
        "--db",
        connection.database,
        "--user",
        connection.user,
        "--schema",
        "public",
        "--sslmode",
        connection.sslmode,
        *args,
    ]


def run_pgschema(
    command: str,
    *args: str,
    connection: Connection,
    mounts: dict[Path, str] | None = None,
) -> int:
    cmd = docker_command(
        command,
        *args,
        connection=connection,
        mounts={DB_DIR: "/db", **(mounts or {})},
        image=get_settings().pgschema_image,
    )
    env = {**os.environ, "PGPASSWORD": connection.password}
    return subprocess.run(cmd, env=env, check=False).returncode


def format_schema() -> None:
    """Fix what sqlfluff can, then lint so what is left shows its file and rule."""
    for action in ("fix", "lint"):
        subprocess.run(
            [sys.executable, "-m", "sqlfluff", action, str(SCHEMA_DIR)],
            cwd=API_DIR,
            check=False,
        )


def next_migration_path() -> Path:
    MIGRATIONS_DIR.mkdir(parents=True, exist_ok=True)
    numbers = [
        int(f.stem) for f in MIGRATIONS_DIR.glob("[0-9][0-9][0-9][0-9][0-9][0-9].sql")
    ]
    return MIGRATIONS_DIR / f"{max(numbers, default=0) + 1:06d}.sql"


def plan_sql(connection: Connection, out_dir: Path) -> tuple[int, str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    out_dir.chmod(0o777)
    returncode = run_pgschema(
        "plan",
        "--file",
        MANIFEST,
        "--output-json",
        "/out/plan.json",
        "--output-sql",
        "/out/plan.sql",
        connection=connection,
        mounts={out_dir: "/out"},
    )
    sql_file = out_dir / "plan.sql"
    return returncode, sql_file.read_text() if sql_file.is_file() else ""


def plan(connection: Connection, *, format: bool = True) -> int:
    if format:
        format_schema()
    generate_manifest(SCHEMA_DIR)
    path = next_migration_path()
    returncode = run_pgschema(
        "plan",
        "--file",
        MANIFEST,
        "--output-sql",
        f"/db/migrations/{path.name}",
        connection=connection,
    )
    if returncode != 0:
        return returncode
    if not path.is_file() or path.stat().st_size == 0:
        path.unlink(missing_ok=True)
        print("No changes detected.")
        return 0
    print(f"Wrote the migration plan to {path.relative_to(ROOT)}")
    return 0


def apply(
    connection: Connection,
    *,
    allow_destructive: bool = False,
    out_dir: Path | None = None,
) -> int:
    generate_manifest(SCHEMA_DIR)
    with TemporaryDirectory() as scratch:
        target = out_dir or Path(scratch)
        target.mkdir(parents=True, exist_ok=True)
        returncode, sql = plan_sql(connection, target)
        if returncode != 0:
            return returncode
        if not sql.strip():
            print(f"No changes: {connection.label} already matches the schema files.")
            return 0
        print(f"Pending changes for {connection.label}:\n\n{sql}")
        findings = destructive_statements(sql)
        if findings and not allow_destructive:
            print("Refusing to apply: the plan could lose data.", file=sys.stderr)
            for finding in findings:
                print(f"  {finding.reason}: {finding.statement}", file=sys.stderr)
            return 2
        return run_pgschema(
            "apply",
            "--plan",
            "/out/plan.json",
            "--auto-approve",
            "--lock-timeout",
            LOCK_TIMEOUT,
            connection=connection,
            mounts={target: "/out"},
        )


def verify(connection: Connection) -> int:
    manifest = SCHEMA_DIR / "manifest.sql"
    if not manifest.is_file() or manifest.read_text() != manifest_text(SCHEMA_DIR):
        print(
            "manifest.sql is out of date: run `hackproof schema plan`.", file=sys.stderr
        )
        return 1
    with TemporaryDirectory() as scratch:
        returncode, sql = plan_sql(connection, Path(scratch))
    if returncode != 0:
        return returncode
    if sql.strip():
        print(
            f"{connection.label} differs from the schema files:\n\n{sql}",
            file=sys.stderr,
        )
        return 1
    print(f"In sync: {connection.label} matches the schema files.")
    return 0
