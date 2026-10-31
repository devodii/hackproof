import asyncio
import logging
from pathlib import Path
import sys

import asyncpg

REPO_ROOT = Path(__file__).resolve().parents[1]
API_SRC = REPO_ROOT / "apps" / "api" / "src"
if str(API_SRC) not in sys.path:
    sys.path.insert(0, str(API_SRC))

from hackproof.config import get_settings

log = logging.getLogger("hackproof.dump_sample")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

OUTPUT_PATH = REPO_ROOT / "data" / "sample" / "sample.sql"


def _fmt(val) -> str:
    if val is None:
        return "NULL"
    if isinstance(val, bool):
        return "true" if val else "false"
    if isinstance(val, (int, float)):
        return str(val)
    if isinstance(val, list):
        items = ", ".join(f"'{str(x).replace("'", "''")}'" for x in val)
        return f"ARRAY[{items}]"
    if isinstance(val, dict):
        import json

        s = json.dumps(val).replace("'", "''")
        return f"'{s}'"
    s = str(val).replace("'", "''")
    return f"'{s}'"


async def dump_sample() -> None:
    settings = get_settings()
    log.info("Connecting to source database %s...", settings.database_url)
    conn = await asyncpg.connect(settings.database_url)

    try:
        # Fetch 10 projects
        projects = await conn.fetch("SELECT * FROM projects ORDER BY contracts DESC, builders DESC LIMIT 10")
        if not projects:
            log.warning("No projects found in database to dump.")
            return

        full_names = [p["full_name"] for p in projects if p["full_name"]]

        repos = await conn.fetch("SELECT * FROM repos WHERE full_name = ANY($1)", full_names)
        contributors = await conn.fetch(
            "SELECT * FROM repo_contributors WHERE full_name = ANY($1)", full_names
        )

        contracts = await conn.fetch(
            "SELECT c.* FROM contracts c "
            "JOIN attribution a ON a.subject_kind = 'contract' AND a.subject = c.contract_id "
            "WHERE a.full_name = ANY($1) "
            "ORDER BY c.deployed_at "
            "LIMIT 20",
            full_names,
        )

        contract_ids = [c["contract_id"] for c in contracts]
        links = await conn.fetch(
            "SELECT * FROM links WHERE full_name = ANY($1) AND subject = ANY($2)",
            full_names,
            contract_ids,
        )

        failed_txs = await conn.fetch("SELECT * FROM failed_txs ORDER BY created_at LIMIT 10")

        lines: list[str] = [
            "-- HackProof Anonymized Local Development Sample Dataset",
            f"-- Generated from active database ({len(projects)} projects, {len(contracts)} contracts)",
            "",
            "BEGIN;",
            "",
        ]

        # Dump Repos
        if repos:
            cols = list(repos[0].keys())
            lines.append(f"INSERT INTO repos ({', '.join(cols)}) VALUES")
            repo_values = []
            for r in repos:
                row_str = "(" + ", ".join(_fmt(r[c]) for c in cols) + ")"
                repo_values.append(row_str)
            lines.append(",\n".join(repo_values))
            lines.append("ON CONFLICT (full_name) DO NOTHING;\n")

        # Dump Projects
        cols = list(projects[0].keys())
        lines.append(f"INSERT INTO projects ({', '.join(cols)}) VALUES")
        proj_values = []
        for p in projects:
            row_str = "(" + ", ".join(_fmt(p[c]) for c in cols) + ")"
            proj_values.append(row_str)
        lines.append(",\n".join(proj_values))
        lines.append("ON CONFLICT (project_id) DO NOTHING;\n")

        # Dump Contributors
        if contributors:
            cols = list(contributors[0].keys())
            lines.append(f"INSERT INTO repo_contributors ({', '.join(cols)}) VALUES")
            c_values = []
            for c in contributors:
                row_str = "(" + ", ".join(_fmt(c[c]) for c in cols) + ")"
                c_values.append(row_str)
            lines.append(",\n".join(c_values))
            lines.append("ON CONFLICT (full_name, login) DO NOTHING;\n")

        # Dump Contracts
        if contracts:
            cols = list(contracts[0].keys())
            lines.append(f"INSERT INTO contracts ({', '.join(cols)}) VALUES")
            ct_values = []
            for ct in contracts:
                row_str = "(" + ", ".join(_fmt(ct[c]) for c in cols) + ")"
                ct_values.append(row_str)
            lines.append(",\n".join(ct_values))
            lines.append("ON CONFLICT (contract_id) DO NOTHING;\n")

        # Dump Links
        if links:
            cols = list(links[0].keys())
            lines.append(f"INSERT INTO links ({', '.join(cols)}) VALUES")
            l_values = []
            for lk in links:
                row_str = "(" + ", ".join(_fmt(lk[c]) for c in cols) + ")"
                l_values.append(row_str)
            lines.append(",\n".join(l_values))
            lines.append("ON CONFLICT (subject_kind, subject, full_name) DO NOTHING;\n")

        # Dump Failed Txs
        if failed_txs:
            cols = list(failed_txs[0].keys())
            lines.append(f"INSERT INTO failed_txs ({', '.join(cols)}) VALUES")
            f_values = []
            for f in failed_txs:
                row_str = "(" + ", ".join(_fmt(f[c]) for c in cols) + ")"
                f_values.append(row_str)
            lines.append(",\n".join(f_values))
            lines.append("ON CONFLICT (tx_hash) DO NOTHING;\n")

        lines.append("COMMIT;\n")

        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_PATH.write_text("\n".join(lines), encoding="utf-8")
        log.info("Successfully dumped sample dataset to %s", OUTPUT_PATH)

    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(dump_sample())
