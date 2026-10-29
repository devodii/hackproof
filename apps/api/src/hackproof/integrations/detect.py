import re
from pathlib import PurePosixPath
from typing import Literal

from pydantic import BaseModel, ConfigDict

from hackproof.github.dependencies import ECOSYSTEM, PARSERS
from hackproof.integrations.catalog import Catalog, Partner

PROSE_SUFFIXES = {".md", ".txt"}

Method = Literal["package", "endpoint"]


class Detection(BaseModel):
    model_config = ConfigDict(frozen=True)

    slug: str
    method: Method
    evidence: str
    path: str


def _normalize(ecosystem: str, name: str) -> str:
    return name.lower().replace("_", "-") if ecosystem == "python" else name


def _declares(ecosystem: str, partner: Partner, declared: dict[str, str | None]) -> list[str]:
    wanted = [_normalize(ecosystem, name) for name in partner.packages.get(ecosystem, [])]
    found = []
    for name in declared:
        normal = _normalize(ecosystem, name)
        if any(
            normal == target or (ecosystem == "go" and normal.startswith(f"{target}/"))
            for target in wanted
        ):
            found.append(name)
    return found


def _endpoint(host: str) -> re.Pattern[str]:
    return re.compile(rf"(?<![\w.-]){re.escape(host)}(?![\w-]|\.\w)", re.IGNORECASE)


def detect(files: dict[str, str], catalog: Catalog, owner: str) -> list[Detection]:
    partners = [
        partner
        for partner in catalog.partners
        if owner.lower() not in {name.lower() for name in partner.github_owners}
    ]
    endpoints = {
        partner.slug: [(host, _endpoint(host)) for host in partner.endpoints]
        for partner in partners
    }
    found: dict[tuple[str, Method, str], Detection] = {}
    for path, text in files.items():
        name = PurePosixPath(path).name
        if name in PARSERS:
            try:
                declared = PARSERS[name](text)
            except (ValueError, KeyError, AttributeError):
                declared = {}
            for partner in partners:
                for package in _declares(ECOSYSTEM[name], partner, declared):
                    found.setdefault(
                        (partner.slug, "package", package),
                        Detection(slug=partner.slug, method="package", evidence=package, path=path),
                    )
        if PurePosixPath(path).suffix in PROSE_SUFFIXES or name.lower().startswith("readme"):
            continue
        for partner in partners:
            for host, pattern in endpoints[partner.slug]:
                if pattern.search(text):
                    found.setdefault(
                        (partner.slug, "endpoint", host),
                        Detection(slug=partner.slug, method="endpoint", evidence=host, path=path),
                    )
    return list(found.values())
