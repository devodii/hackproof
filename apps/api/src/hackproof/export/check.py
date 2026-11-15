from pathlib import Path


def drift(generated: Path, committed: Path) -> list[str]:
    ours = {path.relative_to(generated) for path in generated.rglob("*.yml")}
    theirs = {path.relative_to(committed) for path in committed.rglob("*.yml")}
    found = [f"only in the files: {name}" for name in sorted(theirs - ours)]
    found += [f"only in the database: {name}" for name in sorted(ours - theirs)]
    found += [
        f"differs: {name}"
        for name in sorted(ours & theirs)
        if (generated / name).read_bytes() != (committed / name).read_bytes()
    ]
    return found
