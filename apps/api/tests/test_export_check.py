from pathlib import Path

from hackproof.export.check import drift


def write(root: Path, files: dict[str, str]) -> Path:
    for name, text in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    return root


def test_identical_files_have_no_drift(tmp_path):
    files = {"2026/a.yml": "x: 1\n", "schema.yml": "y: 2\n"}

    assert drift(write(tmp_path / "db", files), write(tmp_path / "repo", files)) == []


def test_drift_names_missing_extra_and_changed_files(tmp_path):
    database = write(
        tmp_path / "db", {"2026/a.yml": "x: 1\n", "2026/new.yml": "n: 1\n"}
    )
    committed = write(
        tmp_path / "repo", {"2026/a.yml": "x: 2\n", "2026/old.yml": "o: 1\n"}
    )

    assert drift(database, committed) == [
        "only in the files: 2026/old.yml",
        "only in the database: 2026/new.yml",
        "differs: 2026/a.yml",
    ]
