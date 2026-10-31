import json
import re
import tomllib
from pathlib import PurePosixPath
from typing import Any

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

OPENZEPPELIN_PACKAGES = {
    "stellar-contracts",
    "openzeppelin-stellar-contracts",
    "openzeppelin_stellar_contracts",
    "@openzeppelin/contracts",
    "@openzeppelin/stellar-contracts",
}

WALLETS_KIT_PACKAGES = {
    "@creit.tech/stellar-wallets-kit",
    "stellar-wallets-kit",
}

FREIGHTER_PACKAGES = {
    "@stellar/freighter-api",
    "freighter-api",
}

PASSKEY_PACKAGES = {
    "passkey-kit",
    "@stellar/passkey-kit",
}


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


def detect_openzeppelin(files: dict[str, str]) -> bool:
    for path, text in files.items():
        name = PurePosixPath(path).name
        if name not in PARSERS:
            continue
        try:
            declared = PARSERS[name](text)
            if any(pkg in declared for pkg in OPENZEPPELIN_PACKAGES):
                return True
        except Exception:
            continue
    return False


def detect_framework(files: dict[str, str]) -> str:
    for path, text in files.items():
        if PurePosixPath(path).name == "package.json":
            try:
                data = json.loads(text)
                deps: dict[str, Any] = {}
                for section in ("dependencies", "devDependencies"):
                    deps.update(data.get(section, {}))
                if "next" in deps:
                    return "Next.js"
                if "vite" in deps:
                    return "Vite"
            except Exception:
                continue
    return "Other"


def detect_ai_tooling(paths: list[str]) -> list[str]:
    found = set()
    for path in paths:
        normalized = "/" + path.strip("/").lower()
        parts = PurePosixPath(path).parts
        name = parts[-1].lower() if parts else ""
        if name == "claude.md":
            found.add("CLAUDE.md")
        elif name == "agents.md":
            found.add("AGENTS.md")
        elif name == ".cursorrules" or ".cursor/rules" in normalized or "cursorrules" in name:
            found.add("Cursor rules")
        elif "copilot-instructions" in normalized:
            found.add("Copilot instructions")
    return sorted(found)


def parse_major_version(spec: str | None) -> str:
    if not spec:
        return "Unknown"
    m = re.search(r"(\d+)", spec)
    if m:
        return f"v{m.group(1)}"
    return "Unknown"
