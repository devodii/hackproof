import re
from collections.abc import Iterable, Sequence
from fnmatch import fnmatchcase
from pathlib import PurePosixPath

from hackproof.github.dependencies import ECOSYSTEM, PARSERS, SKIP_DIRECTORIES
from hackproof.integrations.catalog import Catalog, Partner, Product
from hackproof.integrations.models import AgentDetection, Detection, Method

PROSE_SUFFIXES = {".md", ".txt"}


def _normalize(ecosystem: str, name: str) -> str:
    return name.lower().replace("_", "-") if ecosystem == "python" else name


def _declares(
    ecosystem: str, partner: Product, declared: dict[str, str | None]
) -> list[str]:
    wanted = [
        _normalize(ecosystem, name) for name in partner.packages.get(ecosystem, [])
    ]
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
    found = _detect(files, catalog.partners, owner)
    return found + _profiles(files, catalog.partners, owner, found)


def _profile_hits(files: dict[str, str], partner: Partner) -> list[Detection]:
    profile = partner.profile
    if profile is None:
        return []
    ids = {contract.id: contract for contract in profile.contracts}
    hits: dict[tuple[Method, str], Detection] = {}

    def add(method: Method, evidence: str, path: str) -> None:
        hits.setdefault(
            (method, evidence),
            Detection(slug=partner.slug, method=method, evidence=evidence, path=path),
        )

    for path, text in files.items():
        for contract_id in ids:
            if contract_id in text:
                add("contract", contract_id, path)
        name = PurePosixPath(path).name
        if PurePosixPath(path).suffix in PROSE_SUFFIXES or name.lower().startswith(
            "readme"
        ):
            continue
        if not profile.in_context(text):
            continue
        for signal in profile.signals:
            if any(regex.search(text) for regex in signal.regexes):
                add("signal", signal.slug, path)
        for capture in profile.captures:
            for regex in capture.regexes:
                for match in regex.finditer(text):
                    add("capture", f"{capture.slug}:{match[1]}", path)
    return list(hits.values())


def _profiles(
    files: dict[str, str],
    partners: Sequence[Partner],
    owner: str,
    found: list[Detection],
) -> list[Detection]:
    detections: list[Detection] = []
    for partner in partners:
        if partner.profile is None or owner.lower() in {
            name.lower() for name in partner.github_owners
        }:
            continue
        clients = {
            signal.slug
            for signal in partner.profile.signals
            if signal.group == "client"
        }
        hits = _profile_hits(files, partner)
        present = any(item.slug == partner.slug for item in found) or any(
            hit.method == "contract" or hit.evidence in clients for hit in hits
        )
        if present:
            detections.extend(hits)
    return detections


def detect_tools(
    files: dict[str, str], catalog: Catalog, owner: str
) -> list[Detection]:
    return _detect(files, catalog.tools, owner)


def _detect(
    files: dict[str, str], products: Sequence[Product], owner: str
) -> list[Detection]:
    partners = [
        partner
        for partner in products
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
                        Detection(
                            slug=partner.slug,
                            method="package",
                            evidence=package,
                            path=path,
                        ),
                    )
        if PurePosixPath(path).suffix in PROSE_SUFFIXES or name.lower().startswith(
            "readme"
        ):
            continue
        for partner in partners:
            for host, pattern in endpoints[partner.slug]:
                if pattern.search(text):
                    found.setdefault(
                        (partner.slug, "endpoint", host),
                        Detection(
                            slug=partner.slug,
                            method="endpoint",
                            evidence=host,
                            path=path,
                        ),
                    )
    return list(found.values())


def _matches(path: str, pattern: str) -> bool:
    return fnmatchcase(path, pattern) or fnmatchcase(path, f"*/{pattern}")


def detect_agents(
    paths: Iterable[str], logins: Iterable[str], catalog: Catalog
) -> list[AgentDetection]:
    tracked = [
        path
        for path in paths
        if not SKIP_DIRECTORIES & set(PurePosixPath(path).parts[:-1])
    ]
    people = {login.lower() for login in logins}
    found: list[AgentDetection] = []
    for agent in catalog.agents:
        for pattern in agent.files:
            match = next((path for path in tracked if _matches(path, pattern)), None)
            if match:
                found.append(
                    AgentDetection(
                        slug=agent.slug, method="file", evidence=pattern, path=match
                    )
                )
        found.extend(
            AgentDetection(slug=agent.slug, method="author", evidence=login, path="")
            for login in agent.authors
            if login.lower() in people
        )
    return found
