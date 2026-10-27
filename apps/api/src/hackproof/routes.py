from typing import Annotated, Any

from fastapi import APIRouter, HTTPException, Query

from hackproof import queries
from hackproof.schemas import (
    Builder,
    Contract,
    FailedTx,
    Page,
    Project,
    ProjectDetail,
    Stats,
    WasmUpload,
)

router = APIRouter()

Search = Annotated[str | None, Query(max_length=120)]
Limit = Annotated[int, Query(ge=1, le=200)]
Offset = Annotated[int, Query(ge=0)]
EVERYTHING = 10_000


@router.get("/stats")
async def stats() -> Stats:
    return Stats(**await queries.fetch_stats())


async def _page(resource: queries.Resource, q: str | None, limit: int, offset: int) -> Page[Any]:
    items, total = await queries.list_page(resource, q=q, limit=limit, offset=offset)
    return Page(items=items, total=total)


@router.get("/projects")
async def projects(q: Search = None, limit: Limit = 50, offset: Offset = 0) -> Page[Project]:
    return await _page("projects", q, limit, offset)


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
    found = await _everything("projects", project_id=project_id)
    if not found:
        raise HTTPException(status_code=404, detail="project not found")
    return ProjectDetail(
        project=found[0],
        links=await queries.fetch_links(found[0]["full_name"]) if found[0]["full_name"] else [],
        contracts=await _everything("contracts", project_id=project_id),
        wasm_uploads=await _everything("wasm", project_id=project_id),
        failed_txs=await _everything("failed", project_id=project_id),
    )


@router.get("/builders/{address}")
async def builder(address: str) -> Builder:
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
