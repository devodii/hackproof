from datetime import datetime
from functools import lru_cache
from typing import Literal

import yaml
from pydantic import BaseModel

from hackproof.config import get_settings

Place = Literal["first", "runner-up"]


class Window(BaseModel):
    start: datetime
    pull_start: datetime
    end: datetime


class Discovery(BaseModel):
    github_queries: list[str]
    github_code_queries: list[str]
    github_string_queries: list[str]
    dependency_fingerprints: dict[str, list[str]]
    exclude_owners: list[str]
    exclude_repos: list[str] = []
    known_infra_accounts: list[str]


class Award(BaseModel):
    project_id: str
    place: Place


class Hackathon(BaseModel):
    slug: str
    name: str
    summary: str | None = None
    website: str | None = None
    location: str | None = None
    about: str | None = None
    window: Window
    awards: list[Award] = []
    discovery: Discovery

    def places(self) -> dict[str, Place]:
        return {award.project_id: award.place for award in self.awards}


@lru_cache
def get_hackathon() -> Hackathon:
    with get_settings().hackathon_file.open() as file:
        return Hackathon.model_validate(yaml.safe_load(file))


@lru_cache
def hackathons() -> dict[str, Hackathon]:
    found = [
        Hackathon.model_validate(yaml.safe_load(path.read_text()))
        for path in get_settings().data_dir.glob("*/main.yaml")
    ]
    found.sort(key=lambda hackathon: hackathon.window.start, reverse=True)
    return {hackathon.slug: hackathon for hackathon in found}
