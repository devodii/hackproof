from typing import Annotated

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


@router.get("/projects")
async def projects(q: Search = None, limit: Limit = 50, offset: Offset = 0) -> Page[Project]:
    items, total = await queries.list_projects(q=q, limit=limit, offset=offset)
    return Page(items=items, total=total)


@router.get("/projects/{project_id:path}")
async def project(project_id: str) -> ProjectDetail:
    found, _ = await queries.list_projects(q=None, project_id=project_id, limit=1, offset=0)
    if not found:
        raise HTTPException(status_code=404, detail="project not found")
    contracts, _ = await queries.list_contracts(
        q=None, project_id=project_id, limit=EVERYTHING, offset=0
    )
    wasm, _ = await queries.list_wasm(q=None, project_id=project_id, limit=EVERYTHING, offset=0)
    failed, _ = await queries.list_failed(q=None, project_id=project_id, limit=EVERYTHING, offset=0)
    return ProjectDetail(
        project=found[0], contracts=contracts, wasm_uploads=wasm, failed_txs=failed
    )


@router.get("/contracts")
async def contracts(q: Search = None, limit: Limit = 50, offset: Offset = 0) -> Page[Contract]:
    items, total = await queries.list_contracts(q=q, limit=limit, offset=offset)
    return Page(items=items, total=total)


@router.get("/wasm")
async def wasm(q: Search = None, limit: Limit = 50, offset: Offset = 0) -> Page[WasmUpload]:
    items, total = await queries.list_wasm(q=q, limit=limit, offset=offset)
    return Page(items=items, total=total)


@router.get("/failed")
async def failed(q: Search = None, limit: Limit = 50, offset: Offset = 0) -> Page[FailedTx]:
    items, total = await queries.list_failed(q=q, limit=limit, offset=offset)
    return Page(items=items, total=total)


@router.get("/builders/{address}")
async def builder(address: str) -> Builder:
    kwargs = {"q": None, "account": address, "limit": EVERYTHING, "offset": 0}
    projects_, _ = await queries.list_projects(**kwargs)
    contracts_, _ = await queries.list_contracts(**kwargs)
    wasm_, _ = await queries.list_wasm(**kwargs)
    failed_, _ = await queries.list_failed(**kwargs)
    if not (projects_ or contracts_ or wasm_ or failed_):
        raise HTTPException(status_code=404, detail="no activity in the hack window")
    return Builder(
        address=address,
        projects=projects_,
        contracts=contracts_,
        wasm_uploads=wasm_,
        failed_txs=failed_,
    )
