from typing import Annotated, Any

from pydantic import BaseModel, Field
from pydantic_core import to_jsonable_python

from hackproof import queries
from hackproof.chat.briefs import builder_brief, project_brief, slim
from hackproof.schemas import Tier

Limit = Annotated[int, Field(ge=1, le=25, description="Rows to return")]
Search = Annotated[
    str | None, Field(max_length=120, description="Case-insensitive text to match, or null")
]


class QueryProjects(BaseModel):
    """Find HackMeridian projects. Ordered by evidence strength, then on-chain activity."""

    q: Search = None
    tiers: list[Tier] | None = Field(
        default=None, description="Evidence tiers to include; null means verified and likely"
    )
    limit: Limit = 10


class QueryContracts(BaseModel):
    """List contracts deployed inside the hack window, newest first."""

    q: Search = None
    deployer: str | None = Field(default=None, description="Deploy account (G...)")
    project_id: str | None = Field(default=None, description="A project id such as repo:owner/name")
    limit: Limit = 10


class QueryWasm(BaseModel):
    """List wasm uploads inside the hack window, newest first."""

    q: Search = None
    uploader: str | None = Field(default=None, description="Uploading account (G...)")
    limit: Limit = 10


class QueryFailed(BaseModel):
    """List failed Soroban transactions inside the hack window, newest first."""

    q: Search = None
    account: str | None = Field(default=None, description="Source account (G...)")
    limit: Limit = 10


class GetProject(BaseModel):
    """Load one project in full: its data, stack, on-chain evidence, contributors and contracts."""

    project_id: str = Field(description="A project id such as repo:owner/name")


class GetBuilder(BaseModel):
    """Load one deploy account in full: its projects, contracts and activity counts."""

    address: str = Field(description="Stellar account (G...)")


class GetStats(BaseModel):
    """Headline counts: projects by tier, contracts, builders, contributors, countries."""


class GetTimeline(BaseModel):
    """Contracts deployed per hour across the 27 hour window."""


class GetCountries(BaseModel):
    """Contributors per country across the verified and likely projects."""


TOOLS: dict[str, type[BaseModel]] = {
    "query_projects": QueryProjects,
    "query_contracts": QueryContracts,
    "query_wasm": QueryWasm,
    "query_failed": QueryFailed,
    "get_project": GetProject,
    "get_builder": GetBuilder,
    "get_stats": GetStats,
    "get_timeline": GetTimeline,
    "get_countries": GetCountries,
}

TOOL_SPECS = [
    {
        "name": name,
        "description": (model.__doc__ or "").strip(),
        "input_schema": model.model_json_schema(),
    }
    for name, model in TOOLS.items()
]


async def run_tool(name: str, raw: dict[str, Any]) -> Any:
    args = TOOLS[name].model_validate(raw)
    match args:
        case QueryProjects():
            items, total = await queries.list_page(
                "projects", q=args.q, tiers=args.tiers or ["verified", "likely"], limit=args.limit
            )
        case QueryContracts():
            items, total = await queries.list_page(
                "contracts",
                q=args.q,
                account=args.deployer,
                project_id=args.project_id,
                limit=args.limit,
            )
        case QueryWasm():
            items, total = await queries.list_page(
                "wasm", q=args.q, account=args.uploader, limit=args.limit
            )
        case QueryFailed():
            items, total = await queries.list_page(
                "failed", q=args.q, account=args.account, limit=args.limit
            )
        case GetProject():
            return await project_brief(args.project_id) or {"error": "project not found"}
        case GetBuilder():
            return await builder_brief(args.address) or {"error": "no activity in the hack window"}
        case GetStats():
            return to_jsonable_python(await queries.fetch_stats())
        case GetTimeline():
            return to_jsonable_python(await queries.fetch_timeline())
        case GetCountries():
            return to_jsonable_python(await queries.fetch_countries())
    return to_jsonable_python({"total": total, "items": slim(items)})
