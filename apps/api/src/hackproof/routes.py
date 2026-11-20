from typing import Annotated, Any, Literal

from fastapi import APIRouter, HTTPException, Query

from hackproof import queries
from hackproof.integrations.insights import depths
from hackproof.schemas import (
    AIAgent,
    Builder,
    Contract,
    CountryCount,
    EcosystemTool,
    FailedTx,
    Integration,
    Page,
    Person,
    Project,
    ProjectDetail,
    Stats,
    Tier,
    TimelinePoint,
    WasmUpload,
    Wrapped,
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


async def _page(
    resource: queries.Resource, q: str | None, limit: int, offset: int
) -> Page[Any]:
    items, total = await queries.list_page(resource, q=q, limit=limit, offset=offset)
    return Page(items=items, total=total)


@router.get("/wrapped")
async def wrapped() -> Wrapped:
    return Wrapped(**await queries.fetch_wrapped())


@router.get("/timeline")
async def timeline() -> list[TimelinePoint]:
    return [TimelinePoint(**point) for point in await queries.fetch_timeline()]


@router.get("/countries")
async def countries() -> list[CountryCount]:
    return [CountryCount(**row) for row in await queries.fetch_countries()]


@router.get("/integrations")
async def integrations() -> list[Integration]:
    return [Integration(**row) for row in await queries.fetch_integrations()]


@router.get("/tools")
async def tools() -> list[EcosystemTool]:
    return [EcosystemTool(**row) for row in await queries.fetch_tools()]


@router.get("/agents")
async def agents() -> list[AIAgent]:
    return [AIAgent(**row) for row in await queries.fetch_agents()]


@router.get("/projects")
async def projects(
    q: Search = None,
    tier: Tiers = None,
    track: Annotated[Literal["genesis", "scale"] | None, Query()] = None,
    integration: Annotated[list[str] | None, Query()] = None,
    tool: Annotated[list[str] | None, Query()] = None,
    limit: Limit = 50,
    offset: Offset = 0,
) -> Page[Project]:
    items, total = await queries.list_page(
        "projects",
        q=q,
        tiers=list(tier) if tier else None,
        track=track,
        integrations=integration,
        tools=tool,
        limit=limit,
        offset=offset,
    )
    return Page(items=items, total=total)


@router.get("/contracts")
async def contracts(
    q: Search = None, limit: Limit = 50, offset: Offset = 0
) -> Page[Contract]:
    return await _page("contracts", q, limit, offset)


@router.get("/wasm")
async def wasm(
    q: Search = None, limit: Limit = 50, offset: Offset = 0
) -> Page[WasmUpload]:
    return await _page("wasm", q, limit, offset)


@router.get("/failed")
async def failed(
    q: Search = None, limit: Limit = 50, offset: Offset = 0
) -> Page[FailedTx]:
    return await _page("failed", q, limit, offset)


async def _everything(
    resource: queries.Resource, **filters: str
) -> list[dict[str, Any]]:
    items, _ = await queries.list_page(resource, limit=EVERYTHING, **filters)
    return items


@router.get("/projects/{project_id:path}")
async def project(project_id: str) -> ProjectDetail:
    found = await _everything("projects", project_id=project_id)
    if not found:
        raise HTTPException(status_code=404, detail="project not found")
    uses = (
        await queries.fetch_integration_uses(found[0]["full_name"])
        if found[0]["full_name"]
        else []
    )
    tool_uses = (
        await queries.fetch_tool_uses(found[0]["full_name"])
        if found[0]["full_name"]
        else []
    )
    return ProjectDetail(
        project=found[0],
        links=await queries.fetch_links(found[0]["full_name"])
        if found[0]["full_name"]
        else [],
        integration_uses=uses,
        integration_depths=depths(uses + tool_uses),
        tool_uses=tool_uses,
        contributors=(
            await queries.fetch_contributors(found[0]["full_name"])
            if found[0]["full_name"]
            else []
        ),
        contracts=await _everything("contracts", project_id=project_id),
        wasm_uploads=await _everything("wasm", project_id=project_id),
        failed_txs=await _everything("failed", project_id=project_id),
    )


@router.get("/contributors/{login}")
async def contributor(login: str) -> Person:
    person = await queries.fetch_person(login)
    if person is None:
        raise HTTPException(
            status_code=404, detail="no hackathon project for this contributor"
        )
    return Person(**person)


@router.get("/builders/{address}")
async def builder(address: str) -> Builder:
    result = Builder(
        address=address,
        projects=await _everything("projects", account=address),
        contracts=await _everything("contracts", account=address),
        wasm_uploads=await _everything("wasm", account=address),
        failed_txs=await _everything("failed", account=address),
    )
    if not (
        result.projects or result.contracts or result.wasm_uploads or result.failed_txs
    ):
        raise HTTPException(status_code=404, detail="no activity in the hack window")
    return result
