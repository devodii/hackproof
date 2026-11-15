import re
from collections.abc import Callable
from pathlib import Path

LAYERS = [
    "types",
    "functions",
    "tables",
    "constraints",
    "indexes",
    "views",
    "triggers",
]

OBJECT_RE = {
    "tables": re.compile(r'CREATE TABLE( IF NOT EXISTS)? "?([A-Za-z_][A-Za-z0-9_]*)"?'),
    "views": re.compile(
        r'CREATE (?:OR REPLACE )?VIEW "?([A-Za-z_][A-Za-z0-9_]*)"?', re.IGNORECASE
    ),
}
REFERENCE_RE = {
    "tables": re.compile(r'REFERENCES "?([A-Za-z_][A-Za-z0-9_]*)"?'),
    "views": re.compile(r'(?:FROM|JOIN)\s+"?([A-Za-z_][A-Za-z0-9_]*)"?', re.IGNORECASE),
}


def object_name(layer: str, path: Path) -> str | None:
    match = OBJECT_RE[layer].search(path.read_text())
    return match.group(match.lastindex or 1) if match else None


def order_by_dependency(layer: str, directory: Path) -> list[Path]:
    """
    Objects another object points at must load first, and file names alone do not
    guarantee that. Tables point at each other through REFERENCES, views through
    FROM and JOIN.
    """
    files = sorted(directory.glob("*.sql"))
    by_name = {name: f for f in files if (name := object_name(layer, f))}
    ordered: list[Path] = []
    visited: set[str] = set()

    def visit(name: str) -> None:
        if name in visited:
            return
        visited.add(name)
        path = by_name[name]
        for dependency in REFERENCE_RE[layer].findall(path.read_text()):
            if dependency != name and dependency in by_name:
                visit(dependency)
        ordered.append(path)

    for name in by_name:
        visit(name)
    return ordered


def layer_files(schema_dir: Path, layer: str) -> list[Path]:
    directory = schema_dir / layer
    if not directory.is_dir():
        return []
    ordering: Callable[[], list[Path]] = (
        (lambda: order_by_dependency(layer, directory))
        if layer in OBJECT_RE
        else (lambda: sorted(directory.glob("*.sql")))
    )
    return ordering()


def manifest_text(schema_dir: Path) -> str:
    lines = [
        f"\\i {layer}/{path.name}"
        for layer in LAYERS
        for path in layer_files(schema_dir, layer)
    ]
    return "\n".join(lines) + "\n" if lines else ""


def generate_manifest(schema_dir: Path) -> None:
    (schema_dir / "manifest.sql").write_text(manifest_text(schema_dir))


def schema_sql(schema_dir: Path) -> str:
    paths = [
        schema_dir / line.removeprefix("\\i ").strip()
        for line in (schema_dir / "manifest.sql").read_text().splitlines()
        if line.startswith("\\i ")
    ]
    body = "\n".join(path.read_text() for path in paths)
    return f"SET check_function_bodies = off;\n{body}"
