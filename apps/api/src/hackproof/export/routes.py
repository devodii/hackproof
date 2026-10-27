from typing import Annotated

import yaml
from fastapi import APIRouter, Query, Response

from hackproof.db import pool
from hackproof.export.build import STRICT_TIERS, build_export
from hackproof.export.models import HackathonExport, Tier
from hackproof.export.render import json_schema, to_yaml
from hackproof.hackathon import get_hackathon

router = APIRouter(prefix="/export", tags=["export"])

Tiers = Annotated[
    list[Tier] | None, Query(description="Tiers to include; default is the strict set")
]


async def _export(tiers: list[Tier] | None) -> HackathonExport:
    async with pool().acquire() as connection:
        return await build_export(connection, get_hackathon(), tiers or STRICT_TIERS)


@router.get("/projects.json")
async def projects_json(tier: Tiers = None) -> HackathonExport:
    return await _export(tier)


@router.get("/projects.yml")
async def projects_yaml(tier: Tiers = None) -> Response:
    return Response(to_yaml(await _export(tier)), media_type="application/yaml")


@router.get("/schema.json")
async def schema_json() -> dict:
    return json_schema()


@router.get("/schema.yml")
async def schema_yaml() -> Response:
    text = yaml.safe_dump(json_schema(), sort_keys=False, allow_unicode=True, width=100)
    return Response(text, media_type="application/yaml")
