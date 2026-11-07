import os
from typing import Any

import asyncpg
import httpx

from hackproof.db import open_pool, pool


def _format_delta(current: int, previous: int | None) -> str:
    if previous is None:
        return f"{current}"
    diff = current - previous
    sign = "+" if diff >= 0 else ""
    return f"{current} ({sign}{diff})"


def render_digest(previous: dict[str, Any] | None, current: dict[str, Any]) -> str:
    prev = previous or {}
    lines = ["# HackProof Weekly Digest"]

    if "projects" in current:
        p_curr = current["projects"]
        p_prev = prev.get("projects", {})
        lines.append("")
        lines.append("## Projects & Chain")
        lines.append(
            f"- Verified projects: {_format_delta(p_curr['verified'], p_prev.get('verified'))}"
        )
        lines.append(f"- Likely projects: {_format_delta(p_curr['likely'], p_prev.get('likely'))}")
        lines.append(
            f"- Deployed contracts: {_format_delta(p_curr['contracts'], p_prev.get('contracts'))}"
        )

    if "survival" in current:
        s_curr = current["survival"]
        s_prev = prev.get("survival", {})
        lines.append("")
        lines.append("## Survival")
        lines.append(f"- Active repos: {_format_delta(s_curr['active'], s_prev.get('active'))}")
        lines.append(f"- Total tracked: {_format_delta(s_curr['total'], s_prev.get('total'))}")

    if "graduations" in current:
        g_curr = current["graduations"]
        g_prev = prev.get("graduations", {})
        lines.append("")
        lines.append("## Mainnet Graduations")
        lines.append(
            f"- Graduated projects: {_format_delta(g_curr['count'], g_prev.get('count'))}"
        )

    if "scf_links" in current:
        l_curr = current["scf_links"]
        l_prev = prev.get("scf_links", {})
        lines.append("")
        lines.append("## SCF Links")
        lines.append(f"- Linked awards: {_format_delta(l_curr['count'], l_prev.get('count'))}")

    return "\n".join(lines) + "\n"


async def _table_exists(connection: asyncpg.Connection, name: str) -> bool:
    reg = await connection.fetchval("SELECT to_regclass($1)", f"public.{name}")
    return reg is not None


async def collect_snapshot(connection: asyncpg.Connection) -> dict[str, Any]:
    snapshot: dict[str, Any] = {}
    if await _table_exists(connection, "projects"):
        row = await connection.fetchrow(
            """
            SELECT
                COUNT(*) FILTER (WHERE tier = 'verified') AS verified,
                COUNT(*) FILTER (WHERE tier = 'likely') AS likely,
                COALESCE(SUM(contracts), 0) AS contracts
            FROM projects
            """
        )
        if row:
            snapshot["projects"] = {
                "verified": int(row["verified"]),
                "likely": int(row["likely"]),
                "contracts": int(row["contracts"]),
            }

    if await _table_exists(connection, "survival_points"):
        row = await connection.fetchrow(
            """
            SELECT
                COUNT(*) FILTER (WHERE active) AS active,
                COUNT(*) AS total
            FROM survival_points
            """
        )
        if row:
            snapshot["survival"] = {"active": int(row["active"]), "total": int(row["total"])}

    if await _table_exists(connection, "graduations"):
        count = await connection.fetchval("SELECT COUNT(*) FROM graduations")
        snapshot["graduations"] = {"count": int(count or 0)}

    if await _table_exists(connection, "scf_links"):
        count = await connection.fetchval("SELECT COUNT(*) FROM scf_links")
        snapshot["scf_links"] = {"count": int(count or 0)}

    return snapshot


async def post_or_print_digest(markdown: str, webhook_url: str | None = None) -> None:
    target_url = (
        webhook_url
        or os.environ.get("DISCORD_WEBHOOK_URL")
        or os.environ.get("HACKPROOF_DISCORD_WEBHOOK_URL")
    )
    if target_url:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(target_url, json={"content": markdown})
            response.raise_for_status()
    else:
        print(markdown, end="")


async def run_digest() -> str:
    await open_pool()
    async with pool().acquire() as connection:
        current = await collect_snapshot(connection)
    markdown = render_digest(None, current)
    await post_or_print_digest(markdown)
    return markdown
