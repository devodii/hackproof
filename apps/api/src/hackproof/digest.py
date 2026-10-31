import json
import logging
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx
from pydantic import BaseModel, Field

from hackproof.config import get_settings

logger = logging.getLogger(__name__)


def safe_print(text: str) -> None:
    """Print text safely, replacing unencodable characters if stdout does not support UTF-8."""
    try:
        print(text)
    except UnicodeEncodeError:
        encoding = sys.stdout.encoding or "utf-8"
        print(text.encode(encoding, errors="replace").decode(encoding))


class Graduation(BaseModel):
    project_id: str
    name: str | None = None
    target: str = "mainnet"
    details: str | None = None


class SCFLink(BaseModel):
    project_id: str
    name: str | None = None
    round: str | None = None
    award_amount: str | None = None


class RunSnapshot(BaseModel):
    run_id: str | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    projects_count: int = 0
    contracts_count: int = 0
    builders_count: int = 0
    failed_txs_count: int = 0
    survival_points: dict[str, int] | None = None
    graduations: list[Graduation] | None = None
    scf_links: list[SCFLink] | None = None


def format_delta(delta: int) -> str:
    if delta > 0:
        return f"+{delta}"
    return str(delta)


def generate_digest(prev: RunSnapshot, curr: RunSnapshot) -> str:
    """Generate a clean, deterministic markdown digest comparing two weekly runs."""
    date_str = curr.timestamp.strftime("%Y-%m-%d")
    delta_projects = curr.projects_count - prev.projects_count
    delta_contracts = curr.contracts_count - prev.contracts_count
    delta_builders = curr.builders_count - prev.builders_count
    delta_failed = curr.failed_txs_count - prev.failed_txs_count

    lines: list[str] = [
        f"# 🚀 HackProof Weekly Digest ({date_str})",
        "",
        "### 📊 Ecosystem Growth",
        f"- **Projects**: {curr.projects_count} ({format_delta(delta_projects)} this week)",
        f"- **Contracts**: {curr.contracts_count} ({format_delta(delta_contracts)} this week)",
        f"- **Builders**: {curr.builders_count} ({format_delta(delta_builders)} this week)",
        f"- **Failed Txs**: {curr.failed_txs_count} ({format_delta(delta_failed)} this week)",
    ]

    # Section: Survival Points (skipped if table / data does not exist)
    if prev.survival_points is not None and curr.survival_points is not None:
        movers: list[tuple[str, int, int]] = []
        for pid, curr_pts in curr.survival_points.items():
            prev_pts = prev.survival_points.get(pid, 0)
            diff = curr_pts - prev_pts
            if diff > 0:
                movers.append((pid, curr_pts, diff))

        movers.sort(key=lambda x: x[2], reverse=True)
        if movers:
            lines.append("")
            lines.append("### ⭐ Top Survival Movers")
            for pid, curr_pts, diff in movers[:5]:
                lines.append(f"- **{pid}**: {curr_pts} pts (+{diff} pts)")

    # Section: Graduations (skipped if table / data does not exist)
    if curr.graduations:
        lines.append("")
        lines.append("### 🎓 New Graduations")
        for g in curr.graduations:
            label = g.name or g.project_id
            desc = f" ({g.details})" if g.details else ""
            lines.append(f"- **{label}**: deployed to {g.target}{desc}")

    # Section: SCF Links (skipped if table / data does not exist)
    if curr.scf_links:
        lines.append("")
        lines.append("### 🏆 SCF Highlights")
        for scf in curr.scf_links:
            label = scf.name or scf.project_id
            round_info = f"[{scf.round}] " if scf.round else ""
            award = f" - {scf.award_amount}" if scf.award_amount else ""
            lines.append(f"- **{label}**: {round_info}funded{award}")

    lines.append("")
    lines.append("---")
    lines.append("*Track real-time ecosystem activity on [HackProof](https://hackproof.dev)*")

    return "\n".join(lines)


async def post_to_discord(markdown: str, webhook_url: str) -> bool:
    """Post markdown digest content to Discord webhook."""
    payload = {"content": markdown}
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.post(webhook_url, json=payload)
        resp.raise_for_status()
        return True


def load_runs_from_fixture(fixture_path: Path) -> tuple[RunSnapshot, RunSnapshot]:
    with fixture_path.open("r", encoding="utf-8") as f:
        data: dict[str, Any] = json.load(f)

    prev = RunSnapshot.model_validate(data["previous_run"])
    curr = RunSnapshot.model_validate(data["current_run"])
    return prev, curr


async def run_digest_job(
    fixture_path: Path | None = None,
    webhook_url: str | None = None,
) -> str:
    """Execute weekly digest: generate summary and deliver to Discord or stdout."""
    if fixture_path and fixture_path.exists():
        prev_run, curr_run = load_runs_from_fixture(fixture_path)
    else:
        now = datetime.now(UTC)
        prev_run = RunSnapshot(
            run_id="run-baseline-01",
            timestamp=now,
            projects_count=120,
            contracts_count=85,
            builders_count=78,
            failed_txs_count=12,
        )
        curr_run = RunSnapshot(
            run_id="run-baseline-02",
            timestamp=now,
            projects_count=135,
            contracts_count=98,
            builders_count=89,
            failed_txs_count=15,
        )

    digest = generate_digest(prev_run, curr_run)
    dest_webhook = webhook_url or get_settings().discord_webhook_url

    if dest_webhook:
        try:
            await post_to_discord(digest, dest_webhook)
            logger.info("Successfully delivered weekly digest to Discord webhook.")
        except Exception as e:
            logger.error("Failed to post weekly digest to Discord: %s", e)
            safe_print(digest)
            raise
    else:
        safe_print(digest)

    return digest
