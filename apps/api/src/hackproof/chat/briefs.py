import json
from collections import Counter
from typing import Any, Literal

from pydantic import BaseModel, Field
from pydantic_core import to_jsonable_python

from hackproof import queries
from hackproof.chat.prompts import prompt
from hackproof.hackathon import Place
from hackproof.schemas import Tier

HEAVY_FIELDS = {"dependencies", "owner_avatar"}
SAMPLE = 8
STRICT: list[Tier] = ["verified", "likely"]

PageKind = Literal["home", "project", "builder", "filter"]
Track = Literal["genesis", "scale"]


class Page(BaseModel):
    kind: PageKind
    id: str | None = None
    filters: dict[str, list[str]] | None = None


class ProjectFilters(BaseModel):
    tiers: list[Tier] | None = Field(
        default=None,
        description="Evidence tiers to include; null means verified and likely",
    )
    track: Track | None = Field(
        default=None,
        description="genesis (repo created inside the window) or scale (older repo); null for both",
    )
    integrations: list[str] | None = Field(
        default=None,
        description="Partner slugs from get_integrations; keeps projects using any of them",
    )
    tools: list[str] | None = Field(
        default=None,
        description="Stellar tooling slugs from get_tools; keeps projects using any of them",
    )
    agents: list[str] | None = Field(
        default=None,
        description="AI coding agent slugs from get_agents; keeps projects showing any of them",
    )
    languages: list[str] | None = Field(
        default=None, description="Primary repo languages, such as TypeScript or Rust"
    )
    countries: list[str] | None = Field(
        default=None, description="ISO 3166-1 alpha-2 codes of the repo owner's country"
    )
    activity: list[Literal["contracts", "failed"]] | None = Field(
        default=None,
        description="contracts keeps projects that deployed contracts; failed keeps projects "
        "with failed transactions",
    )
    awards: list[Place] | None = Field(
        default=None,
        description="first or runner-up keeps projects that won that award",
    )

    def list_args(self) -> dict[str, Any]:
        return {
            "tiers": self.tiers or STRICT,
            "track": self.track,
            "integrations": self.integrations,
            "tools": self.tools,
            "agents": self.agents,
            "languages": self.languages,
            "countries": self.countries,
            "activity": self.activity,
            "awards": self.awards,
        }


PAGE_FILTERS = {
    "tier": "tiers",
    "partner": "integrations",
    "tool": "tools",
    "agent": "agents",
    "language": "languages",
    "country": "countries",
    "activity": "activity",
    "award": "awards",
}


def slim(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            **{k: v for k, v in item.items() if k not in HEAVY_FIELDS},
            **(
                {"stack": list((item["dependencies"] or {}).get("packages", {}))}
                if "dependencies" in item
                else {}
            ),
        }
        for item in items
    ]


async def project_brief(project_id: str) -> dict[str, Any] | None:
    found, _ = await queries.list_page("projects", project_id=project_id, limit=1)
    if not found:
        return None
    project = found[0]
    full_name = project["full_name"]
    contracts, contract_total = await queries.list_page(
        "contracts", project_id=project_id, limit=SAMPLE
    )
    links = await queries.fetch_links(full_name) if full_name else []
    contributors = await queries.fetch_contributors(full_name) if full_name else []
    return to_jsonable_python(
        {
            "project": slim([project])[0],
            "evidence": [
                {k: link[k] for k in ("subject_kind", "subject", "method", "path")}
                for link in links
                if link["method"] != "footprint"
            ][:SAMPLE],
            "contributors": [
                {k: c[k] for k in ("login", "contributions", "country")}
                for c in contributors[:SAMPLE]
            ],
            "contracts": {"total": contract_total, "latest": slim(contracts)},
        }
    )


async def builder_brief(address: str) -> dict[str, Any] | None:
    projects, project_total = await queries.list_page(
        "projects", account=address, limit=SAMPLE
    )
    contracts, contract_total = await queries.list_page(
        "contracts", account=address, limit=SAMPLE
    )
    _, wasm_total = await queries.list_page("wasm", account=address, limit=1)
    _, failed_total = await queries.list_page("failed", account=address, limit=1)
    if not (project_total or contract_total or wasm_total or failed_total):
        return None
    return to_jsonable_python(
        {
            "address": address,
            "projects": {"total": project_total, "items": slim(projects)},
            "contracts": {"total": contract_total, "latest": slim(contracts)},
            "wasm_uploads": wasm_total,
            "failed_txs": failed_total,
        }
    )


def _top(counter: Counter[str], size: int) -> list[dict[str, Any]]:
    return [
        {"name": name, "projects": count} for name, count in counter.most_common(size)
    ]


async def summarize_view(filters: ProjectFilters) -> dict[str, Any]:
    items, total = await queries.list_page(
        "projects", **filters.list_args(), limit=10_000
    )
    topics: Counter[str] = Counter()
    stack: Counter[str] = Counter()
    partners: Counter[str] = Counter()
    tooling: Counter[str] = Counter()
    agents: Counter[str] = Counter()
    for item in items:
        topics.update(topic.lower() for topic in item["topics"] or [])
        stack.update(list((item["dependencies"] or {}).get("packages", {})))
        partners.update(item["integrations"])
        tooling.update(item["tools"])
        agents.update(item["agents"])
    return {
        "total": total,
        "by_tier": dict(Counter(item["tier"] for item in items)),
        "by_track": dict(Counter(item["track"] for item in items)),
        "contracts": sum(item["contracts"] for item in items),
        "wasm_uploads": sum(item["wasm_uploads"] for item in items),
        "languages": _top(
            Counter(item["language"] for item in items if item["language"]), 10
        ),
        "topics": _top(topics, 20),
        "stellar_packages": _top(stack, 15),
        "integrations": _top(partners, 15),
        "stellar_tooling": _top(tooling, 10),
        "ai_agents": _top(agents, 10),
        "countries": _top(
            Counter(item["country"] for item in items if item["country"]), 10
        ),
        "descriptions": [
            {"project_id": item["project_id"], "description": item["description"][:140]}
            for item in items
            if item["description"]
        ][:25],
    }


def view_filters(selected: dict[str, list[str]]) -> ProjectFilters:
    known = {
        PAGE_FILTERS[key]: values[:20]
        for key, values in selected.items()
        if key in PAGE_FILTERS
    }
    tracks = selected.get("track", [])
    return ProjectFilters.model_validate(
        {**known, "track": tracks[0] if len(tracks) == 1 else None}
    )


async def filter_brief(selected: dict[str, list[str]]) -> str:
    filters = view_filters(selected)
    summary = await summarize_view(filters)
    return prompt(
        "page-filter",
        filters=json.dumps(selected),
        data=json.dumps(to_jsonable_python(summary), default=str),
    )


async def describe_page(page: Page | None) -> str:
    if page is None:
        return ""
    if page.kind == "home":
        return prompt("page-home")
    if page.kind == "filter":
        return await filter_brief(page.filters or {})
    if not page.id:
        return ""

    if page.kind == "project":
        brief = await project_brief(page.id)
        subject, pronoun = f"the project {page.id}", "this project"
    else:
        brief = await builder_brief(page.id)
        subject, pronoun = f"the builder {page.id}", "this builder"
    if brief is None:
        return prompt("page-empty", subject=subject)
    return prompt(
        "page-entity",
        subject=subject,
        pronoun=pronoun,
        data=json.dumps(brief, default=str),
    )
