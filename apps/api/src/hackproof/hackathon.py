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
    known_infra_accounts: list[str]


class Award(BaseModel):
    project_id: str
    place: Place


class Hackathon(BaseModel):
    slug: str
    name: str
    window: Window
    awards: list[Award] = []
    discovery: Discovery


@lru_cache
def get_hackathon() -> Hackathon:
    with get_settings().hackathon_file.open() as file:
        return Hackathon.model_validate(yaml.safe_load(file))


def places() -> dict[str, Place]:
    return {award.project_id: award.place for award in get_hackathon().awards}
