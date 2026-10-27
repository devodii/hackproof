import json
import re
import tomllib
from pathlib import PurePosixPath

from hackproof.github.models import DependencyFingerprint

MANIFESTS = {"Cargo.toml", "package.json", "requirements.txt", "pyproject.toml", "go.mod"}
ECOSYSTEM = {
    "Cargo.toml": "rust",
    "package.json": "js",
    "requirements.txt": "python",
    "pyproject.toml": "python",
    "go.mod": "go",
}
REQUIREMENT = re.compile(r"^([A-Za-z0-9_.-]+)\s*(?:[=~<>!]=?\s*([\w.*-]+))?")
GO_REQUIRE = re.compile(r"^\s*(?:require\s+)?(\S+)\s+(v[\w.+-]+)", re.MULTILINE)


def _cargo(text: str) -> dict[str, str | None]:
    data = tomllib.loads(text)
    tables = [data.get("dependencies", {}), data.get("dev-dependencies", {})]
    tables.append(data.get("workspace", {}).get("dependencies", {}))
    found: dict[str, str | None] = {}
    for table in tables:
        for name, spec in table.items():
            found[name] = spec if isinstance(spec, str) else (spec or {}).get("version")
    return found


def _package_json(text: str) -> dict[str, str | None]:
    data = json.loads(text)
    found: dict[str, str | None] = {}
    for section in ("dependencies", "devDependencies", "peerDependencies"):
        found.update(data.get(section, {}))
    return found


def _requirements(text: str) -> dict[str, str | None]:
    found: dict[str, str | None] = {}
    for line in text.splitlines():
        if match := REQUIREMENT.match(line.strip()):
            found[match[1]] = match[2]
    return found


def _pyproject(text: str) -> dict[str, str | None]:
    data = tomllib.loads(text)
    found = _requirements("\n".join(data.get("project", {}).get("dependencies", [])))
    for name, spec in data.get("tool", {}).get("poetry", {}).get("dependencies", {}).items():
        found[name] = spec if isinstance(spec, str) else (spec or {}).get("version")
    return found


def _go_mod(text: str) -> dict[str, str | None]:
    return {match[1]: match[2] for match in GO_REQUIRE.finditer(text)}


PARSERS = {
    "Cargo.toml": _cargo,
    "package.json": _package_json,
    "requirements.txt": _requirements,
    "pyproject.toml": _pyproject,
    "go.mod": _go_mod,
}


def fingerprint(files: dict[str, str], wanted: dict[str, list[str]]) -> DependencyFingerprint:
    result = DependencyFingerprint()
    for path, text in files.items():
        name = PurePosixPath(path).name
        if name not in PARSERS:
            continue
        try:
            declared = PARSERS[name](text)
        except (ValueError, KeyError, AttributeError):
            continue
        ecosystem = ECOSYSTEM[name]
        for package in wanted.get(ecosystem, []):
            if package in declared:
                result.packages[package] = declared[package]
                if ecosystem not in result.ecosystems:
                    result.ecosystems.append(ecosystem)
    return result
