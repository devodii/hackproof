from typing import Annotated, Any, Literal

import httpx
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from hackproof import queries
from hackproof.config import get_settings
from hackproof.queries import is_hidden
from hackproof.schemas import (
    Builder,
    Contract,
    CountryCount,
    FailedTx,
    Integration,
    Page,
    Project,
    ProjectDetail,
    Stats,
    Tier,
    TimelinePoint,
    WasmUpload,
)

router = APIRouter()

Search = Annotated[str | None, Query(max_length=120)]
Tiers = Annotated[list[Tier] | None, Query()]
Limit = Annotated[int, Query(ge=1, le=200)]
Offset = Annotated[int, Query(ge=0)]
EVERYTHING = 10_000


@router.get("/stats")
async def stats() -> Stats:
    return Stats(**await queries.fetch_stats())


async def _page(resource: queries.Resource, q: str | None, limit: int, offset: int) -> Page[Any]:
    items, total = await queries.list_page(resource, q=q, limit=limit, offset=offset)
    return Page(items=items, total=total)


@router.get("/timeline")
async def timeline() -> list[TimelinePoint]:
    return [TimelinePoint(**point) for point in await queries.fetch_timeline()]


@router.get("/countries")
async def countries() -> list[CountryCount]:
    return [CountryCount(**row) for row in await queries.fetch_countries()]


@router.get("/integrations")
async def integrations() -> list[Integration]:
    return [Integration(**row) for row in await queries.fetch_integrations()]


@router.get("/projects")
async def projects(
    q: Search = None,
    tier: Tiers = None,
    track: Annotated[Literal["genesis", "scale"] | None, Query()] = None,
    integration: Annotated[list[str] | None, Query()] = None,
    limit: Limit = 50,
    offset: Offset = 0,
) -> Page[Project]:
    items, total = await queries.list_page(
        "projects",
        q=q,
        tiers=list(tier) if tier else None,
        track=track,
        integrations=integration,
        limit=limit,
        offset=offset,
    )
    return Page(items=items, total=total)


@router.get("/contracts")
async def contracts(q: Search = None, limit: Limit = 50, offset: Offset = 0) -> Page[Contract]:
    return await _page("contracts", q, limit, offset)


@router.get("/wasm")
async def wasm(q: Search = None, limit: Limit = 50, offset: Offset = 0) -> Page[WasmUpload]:
    return await _page("wasm", q, limit, offset)


@router.get("/failed")
async def failed(q: Search = None, limit: Limit = 50, offset: Offset = 0) -> Page[FailedTx]:
    return await _page("failed", q, limit, offset)


async def _everything(resource: queries.Resource, **filters: str) -> list[dict[str, Any]]:
    items, _ = await queries.list_page(resource, limit=EVERYTHING, **filters)
    return items


@router.get("/projects/{project_id:path}")
async def project(project_id: str) -> ProjectDetail:
    if is_hidden(project_id):
        raise HTTPException(status_code=404, detail="project not found")
    found = await _everything("projects", project_id=project_id)
    if not found:
        raise HTTPException(status_code=404, detail="project not found")
    return ProjectDetail(
        project=found[0],
        links=await queries.fetch_links(found[0]["full_name"]) if found[0]["full_name"] else [],
        integration_uses=(
            await queries.fetch_integration_uses(found[0]["full_name"])
            if found[0]["full_name"]
            else []
        ),
        contributors=(
            await queries.fetch_contributors(found[0]["full_name"]) if found[0]["full_name"] else []
        ),
        contracts=await _everything("contracts", project_id=project_id),
        wasm_uploads=await _everything("wasm", project_id=project_id),
        failed_txs=await _everything("failed", project_id=project_id),
    )


@router.get("/builders/{address}")
async def builder(address: str) -> Builder:
    if is_hidden(address):
        raise HTTPException(status_code=404, detail="no activity in the hack window")
    result = Builder(
        address=address,
        projects=await _everything("projects", account=address),
        contracts=await _everything("contracts", account=address),
        wasm_uploads=await _everything("wasm", account=address),
        failed_txs=await _everything("failed", account=address),
    )
    if not (result.projects or result.contracts or result.wasm_uploads or result.failed_txs):
        raise HTTPException(status_code=404, detail="no activity in the hack window")
    return result


class OptOutRequest(BaseModel):
    project_id: str
    handle: str
    reason: str | None = None


class OptOutResponse(BaseModel):
    status: str = "ok"
    message: str = "We honor opt outs within 24h."
    issue_url: str | None = None


@router.post("/opt-out")
async def opt_out(req: OptOutRequest) -> OptOutResponse:
    project_id = req.project_id.strip()
    handle = req.handle.strip().lstrip("@")
    if not project_id or not handle:
        raise HTTPException(status_code=400, detail="project_id and handle are required")

    settings = get_settings()
    token = settings.opt_out_github_token or (
        settings.github_tokens[0] if settings.github_tokens else None
    )

    issue_title = f"Opt out request: {project_id}"
    issue_body = (
        f"### Opt Out Request\n\n"
        f"- **Project ID**: {project_id}\n"
        f"- **GitHub Handle**: @{handle}\n"
        f"- **Reason**: {req.reason or 'Not specified'}\n\n"
        f"Please remove this project from the index.\n\n"
        f"> We honor opt outs within 24h."
    )

    issue_url = None
    if token:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.post(
                    "https://api.github.com/repos/devodii/hackproof/issues",
                    headers={
                        "Authorization": f"token {token}",
                        "Accept": "application/vnd.github+json",
                        "User-Agent": "HackProof-OptOut",
                    },
                    json={
                        "title": issue_title,
                        "body": issue_body,
                        "labels": ["opt-out"],
                    },
                )
                if resp.status_code == 201:
                    issue_url = resp.json().get("html_url")
        except Exception:
            pass

    return OptOutResponse(
        status="ok",
        message="We honor opt outs within 24h.",
        issue_url=issue_url,
    )
