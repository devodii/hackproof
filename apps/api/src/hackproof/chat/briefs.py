import json
from typing import Any, Literal

from pydantic import BaseModel
from pydantic_core import to_jsonable_python

from hackproof import queries
from hackproof.chat.prompts import prompt

HEAVY_FIELDS = {"dependencies", "owner_avatar"}
SAMPLE = 8

PageKind = Literal["home", "project", "builder"]


class Page(BaseModel):
    kind: PageKind
    id: str | None = None


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
    projects, project_total = await queries.list_page("projects", account=address, limit=SAMPLE)
    contracts, contract_total = await queries.list_page("contracts", account=address, limit=SAMPLE)
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


async def describe_page(page: Page | None) -> str:
    if page is None:
        return ""
    if page.kind == "home":
        return prompt("page-home")
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
        "page-entity", subject=subject, pronoun=pronoun, data=json.dumps(brief, default=str)
    )
