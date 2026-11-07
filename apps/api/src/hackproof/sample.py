from datetime import datetime
import json
import logging
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict

from hackproof.config import get_settings
from hackproof.db import close_pool, open_pool, pool

logger = logging.getLogger(__name__)

PRIVATE_REPO_COLUMNS = {"owner_avatar", "owner_location", "country"}
PRIVATE_CONTRIBUTOR_COLUMNS = {"avatar_url"}


class SampleSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    projects: int
    contracts: int
    loaded: bool


def default_sample_path() -> Path:
    return get_settings().data_dir / "sample" / "sample.sql"


def sanitize_repo_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        key: (None if key in PRIVATE_REPO_COLUMNS else val)
        for key, val in row.items()
    }


def sanitize_contributor_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        key: (None if key in PRIVATE_CONTRIBUTOR_COLUMNS else val)
        for key, val in row.items()
    }


def _sql_literal(value: Any) -> str:
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, datetime):
        return f"'{value.isoformat()}'"
    if isinstance(value, list):
        items = ", ".join(_sql_literal(str(item)) for item in value)
        return f"ARRAY[{items}]::text[]"
    if isinstance(value, dict):
        encoded = json.dumps(value).replace("'", "''")
        return f"'{encoded}'::jsonb"
    escaped = str(value).replace("'", "''")
    return f"'{escaped}'"


def format_insert_block(
    table: str,
    columns: list[str],
    rows: list[dict[str, Any]],
    conflict_cols: list[str],
) -> str:
    if not rows:
        return ""
    col_list = ", ".join(columns)
    values_lines = []
    for row in rows:
        vals = ", ".join(_sql_literal(row.get(col)) for col in columns)
        values_lines.append(f"    ({vals})")
    conflict = ", ".join(conflict_cols)
    body = ",\n".join(values_lines)
    return (
        f"INSERT INTO {table} ({col_list}) VALUES\n"
        f"{body}\n"
        f"ON CONFLICT ({conflict}) DO NOTHING;\n"
    )


async def load_sample_if_empty(sql_path: Path | None = None) -> SampleSummary:
    target = sql_path or default_sample_path()
    async with pool().acquire() as conn:
        existing = await conn.fetchval("SELECT count(*) FROM projects")
        if existing and existing > 0:
            contracts_count = await conn.fetchval("SELECT count(*) FROM contracts")
            logger.info("projects table already has %d rows; skipping sample seed", existing)
            return SampleSummary(
                projects=int(existing),
                contracts=int(contracts_count or 0),
                loaded=False,
            )
        sql_text = target.read_text(encoding="utf-8")
        async with conn.transaction():
            await conn.execute(sql_text)
        projects_count = await conn.fetchval("SELECT count(*) FROM projects")
        contracts_count = await conn.fetchval("SELECT count(*) FROM contracts")
        logger.info(
            "loaded sample dataset (%d projects, %d contracts)",
            projects_count,
            contracts_count,
        )
        return SampleSummary(
            projects=int(projects_count or 0),
            contracts=int(contracts_count or 0),
            loaded=True,
        )


async def dump_sample_from_db(
    output_path: Path | None = None,
    project_limit: int = 10,
    contract_limit: int = 20,
) -> Path:
    target = output_path or default_sample_path()
    async with pool().acquire() as conn:
        project_rows = [
            dict(r)
            for r in await conn.fetch(
                "SELECT * FROM projects ORDER BY contracts DESC, project_id LIMIT $1",
                project_limit,
            )
        ]
        full_names = [r["full_name"] for r in project_rows if r.get("full_name")]
        repo_rows = [
            sanitize_repo_row(dict(r))
            for r in await conn.fetch(
                "SELECT * FROM repos WHERE full_name = ANY($1::text[]) ORDER BY full_name",
                full_names,
            )
        ]
        contract_rows = [
            dict(r)
            for r in await conn.fetch(
                "SELECT * FROM contracts ORDER BY deployed_at ASC LIMIT $1",
                contract_limit,
            )
        ]
        link_rows = [
            dict(r)
            for r in await conn.fetch(
                "SELECT * FROM links WHERE full_name = ANY($1::text[])"
                " ORDER BY full_name, subject_kind, subject",
                full_names,
            )
        ]
        contributor_rows = [
            sanitize_contributor_row(dict(r))
            for r in await conn.fetch(
                "SELECT * FROM repo_contributors WHERE full_name = ANY($1::text[])"
                " ORDER BY full_name, contributions DESC",
                full_names,
            )
        ]

    blocks = [
        "-- HackProof anonymized sample dataset\n"
        "-- Contains only public GitHub handles and public testnet contract metadata.\n",
    ]
    if repo_rows:
        blocks.append(
            format_insert_block("repos", list(repo_rows[0].keys()), repo_rows, ["full_name"])
        )
    if project_rows:
        blocks.append(
            format_insert_block(
                "projects", list(project_rows[0].keys()), project_rows, ["project_id"]
            )
        )
    if contract_rows:
        blocks.append(
            format_insert_block(
                "contracts", list(contract_rows[0].keys()), contract_rows, ["contract_id"]
            )
        )
    if link_rows:
        blocks.append(
            format_insert_block(
                "links",
                list(link_rows[0].keys()),
                link_rows,
                ["subject_kind", "subject", "full_name"],
            )
        )
    if contributor_rows:
        blocks.append(
            format_insert_block(
                "repo_contributors",
                list(contributor_rows[0].keys()),
                contributor_rows,
                ["full_name", "login"],
            )
        )

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(b for b in blocks if b), encoding="utf-8")
    return target


async def run_seed(sql_path: Path | None = None) -> SampleSummary:
    await open_pool()
    try:
        return await load_sample_if_empty(sql_path)
    finally:
        await close_pool()


async def run_dump_sample(output_path: Path | None = None) -> Path:
    await open_pool()
    try:
        return await dump_sample_from_db(output_path)
    finally:
        await close_pool()
