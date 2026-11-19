import logging
from pathlib import Path
from urllib.parse import unquote

import asyncpg
import yaml
from pydantic import BaseModel, ConfigDict

from hackproof.export.files import EVENT_FILE, ProjectFile
from hackproof.sql_loader import load_sql

log = logging.getLogger("hackproof.export")


class Section(BaseModel):
    model_config = ConfigDict(frozen=True)

    delete: str
    insert: str


RESTORED = {
    "integrations": Section(
        delete="github/delete_integrations", insert="github/insert_integration"
    ),
    "tools": Section(delete="github/delete_tools", insert="github/insert_tool"),
    "agents": Section(delete="github/delete_agents", insert="github/insert_agent"),
}

FROM_DATABASE = {
    "event",
    "canonical_id",
    "repo_url",
    "name",
    "description",
    "homepage",
    "language",
    "license",
    "topics",
    "created_at",
    "owner",
    "track",
    "track_declared",
    "award",
    "evidence_tier",
    "commits_in_window",
    "stack",
    "chain",
    "contributors",
}


def full_name(repo_url: str) -> str:
    return repo_url.removeprefix("https://github.com/")


def path_of(repo_url: str, file_url: str | None) -> str:
    if file_url is None:
        return ""
    prefix = f"{repo_url}/blob/HEAD/"
    return (
        unquote(file_url.removeprefix(prefix))
        if file_url.startswith(prefix)
        else file_url
    )


def load_files(root: Path) -> list[ProjectFile]:
    return [
        ProjectFile.model_validate(yaml.safe_load(path.read_text()))
        for path in sorted(root.glob("*/*.yml"))
        if path.name != EVENT_FILE
    ]


async def restore(connection: asyncpg.Connection, files: list[ProjectFile]) -> int:
    async with connection.transaction():
        for project in files:
            name = full_name(project.repo_url)
            for key, section in RESTORED.items():
                await connection.execute(load_sql(section.delete), name)
                await connection.executemany(
                    load_sql(section.insert),
                    [
                        (
                            name,
                            entry.slug,
                            item.method,
                            item.detail,
                            path_of(project.repo_url, item.file_url),
                        )
                        for entry in getattr(project, key)
                        for item in entry.evidence
                    ],
                )
    return len(files)
