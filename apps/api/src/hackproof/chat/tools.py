from collections import Counter
from typing import Annotated, Any, Literal

from pydantic import BaseModel, Field
from pydantic_core import to_jsonable_python

from hackproof import queries
from hackproof.chat.briefs import builder_brief, project_brief, slim
from hackproof.schemas import Tier

Track = Literal["genesis", "scale"]
STRICT = ["verified", "likely"]
WEB_SEARCH = {"type": "web_search_20250305", "name": "web_search", "max_uses": 3}

Limit = Annotated[int, Field(ge=1, le=25, description="Rows to return")]
Offset = Annotated[int, Field(ge=0, le=5000, description="Rows to skip, for paging")]
Search = Annotated[
    str | None, Field(max_length=120, description="Case-insensitive text to match, or null")
]


class QueryProjects(BaseModel):
    """Find HackMeridian projects. Ordered by evidence strength, then on-chain activity."""

    q: Search = None
    tiers: list[Tier] | None = Field(
        default=None, description="Evidence tiers to include; null means verified and likely"
    )
    track: Track | None = Field(
        default=None,
        description="genesis (repo created inside the window) or scale (older repo); null for both",
    )
    integrations: list[str] | None = Field(
        default=None,
        description="Partner slugs from get_integrations; keeps projects using any of them",
    )
    limit: Limit = 10
    offset: Offset = 0


class QueryContracts(BaseModel):
    """List contracts deployed inside the hack window, newest first."""

    q: Search = None
    deployer: str | None = Field(default=None, description="Deploy account (G...)")
    project_id: str | None = Field(default=None, description="A project id such as repo:owner/name")
    limit: Limit = 10
    offset: Offset = 0


class QueryWasm(BaseModel):
    """List wasm uploads inside the hack window, newest first."""

    q: Search = None
    uploader: str | None = Field(default=None, description="Uploading account (G...)")
    limit: Limit = 10
    offset: Offset = 0


class QueryFailed(BaseModel):
    """List failed Soroban transactions inside the hack window, newest first."""

    q: Search = None
    account: str | None = Field(default=None, description="Source account (G...)")
    limit: Limit = 10
    offset: Offset = 0


class SummarizeProjects(BaseModel):
    """Aggregate every matching project: counts by tier and track, on chain totals, top
    languages, topics, Stellar packages and countries, plus a sample of descriptions. Use this
    for any breakdown or "what are they building" question."""

    tiers: list[Tier] | None = Field(
        default=None, description="Evidence tiers to include; null means verified and likely"
    )
    track: Track | None = Field(default=None, description="genesis, scale, or null for both")
    integrations: list[str] | None = Field(
        default=None,
        description="Partner slugs from get_integrations; keeps projects using any of them",
    )


class GetProject(BaseModel):
    """Load one project in full: its data, stack, on-chain evidence, contributors and contracts."""

    project_id: str = Field(description="A project id such as repo:owner/name")


class GetBuilder(BaseModel):
    """Load one deploy account in full: its projects, contracts and activity counts."""

    address: str = Field(description="Stellar account (G...)")


class GetIntegrations(BaseModel):
    """List the Stellar ecosystem partners we detect (slug, name, category) with how many
    verified and likely projects use each. Detection comes from dependency manifests and API
    hosts in code, not from READMEs."""


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
    "summarize_projects": SummarizeProjects,
    "get_project": GetProject,
    "get_builder": GetBuilder,
    "get_integrations": GetIntegrations,
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


def _top(counter: Counter[str], size: int) -> list[dict[str, Any]]:
    return [{"name": name, "projects": count} for name, count in counter.most_common(size)]


async def summarize(args: SummarizeProjects) -> dict[str, Any]:
    items, total = await queries.list_page(
        "projects",
        tiers=args.tiers or STRICT,
        track=args.track,
        integrations=args.integrations,
        limit=10_000,
    )
    topics: Counter[str] = Counter()
    stack: Counter[str] = Counter()
    partners: Counter[str] = Counter()
    for item in items:
        topics.update(topic.lower() for topic in item["topics"] or [])
        stack.update(list((item["dependencies"] or {}).get("packages", {})))
        partners.update(item["integrations"])
    return {
        "total": total,
        "by_tier": dict(Counter(item["tier"] for item in items)),
        "by_track": dict(Counter(item["track"] for item in items)),
        "contracts": sum(item["contracts"] for item in items),
        "wasm_uploads": sum(item["wasm_uploads"] for item in items),
        "languages": _top(Counter(item["language"] for item in items if item["language"]), 10),
        "topics": _top(topics, 20),
        "stellar_packages": _top(stack, 15),
        "integrations": _top(partners, 15),
        "countries": _top(Counter(item["country"] for item in items if item["country"]), 10),
        "descriptions": [
            {"project_id": item["project_id"], "description": item["description"][:140]}
            for item in items
            if item["description"]
        ][:25],
    }


async def run_tool(name: str, raw: dict[str, Any]) -> Any:
    args = TOOLS[name].model_validate(raw)
    match args:
        case QueryProjects():
            items, total = await queries.list_page(
                "projects",
                q=args.q,
                tiers=args.tiers or STRICT,
                track=args.track,
                integrations=args.integrations,
                limit=args.limit,
                offset=args.offset,
            )
        case QueryContracts():
            items, total = await queries.list_page(
                "contracts",
                q=args.q,
                account=args.deployer,
                project_id=args.project_id,
                limit=args.limit,
                offset=args.offset,
            )
        case QueryWasm():
            items, total = await queries.list_page(
                "wasm", q=args.q, account=args.uploader, limit=args.limit, offset=args.offset
            )
        case QueryFailed():
            items, total = await queries.list_page(
                "failed", q=args.q, account=args.account, limit=args.limit, offset=args.offset
            )
        case SummarizeProjects():
            return to_jsonable_python(await summarize(args))
        case GetProject():
            return await project_brief(args.project_id) or {"error": "project not found"}
        case GetBuilder():
            return await builder_brief(args.address) or {"error": "no activity in the hack window"}
        case GetIntegrations():
            return to_jsonable_python(await queries.fetch_integrations())
        case GetStats():
            return to_jsonable_python(await queries.fetch_stats())
        case GetTimeline():
            return to_jsonable_python(await queries.fetch_timeline())
        case GetCountries():
            return to_jsonable_python(await queries.fetch_countries())
    return to_jsonable_python({"total": total, "items": slim(items)})
