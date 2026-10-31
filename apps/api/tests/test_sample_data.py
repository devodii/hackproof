import re
from pathlib import Path


def test_sample_sql_integrity():
    repo_root = Path(__file__).resolve().parents[3]
    sample_sql = repo_root / "data" / "sample" / "sample.sql"

    assert sample_sql.exists(), f"Sample SQL must exist at {sample_sql}"
    content = sample_sql.read_text(encoding="utf-8")

    assert "BEGIN;" in content
    assert "COMMIT;" in content

    # Acceptance criteria: 10 projects, 20 contracts
    projects = re.findall(r"\('repo:[^']+'", content)
    assert len(projects) >= 10, f"Expected at least 10 projects, found {len(projects)}"

    contracts = re.findall(r"\('C[A-Z0-9]{55}'", content)
    assert len(contracts) >= 20, f"Expected at least 20 contracts, found {len(contracts)}"

    # Acceptance criteria: Contains no data beyond public GitHub handles / testnet
    assert "password" not in content.lower()
    assert "secret" not in content.lower()
    # Ensure no personal emails leaked
    emails = re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", content)
    assert len(emails) == 0, f"Found leaked emails in sample SQL: {emails}"


def test_local_dev_docs_commands():
    repo_root = Path(__file__).resolve().parents[3]
    doc = repo_root / "docs" / "local-dev.md"

    assert doc.exists(), f"local-dev.md must exist at {doc}"
    text = doc.read_text(encoding="utf-8")

    assert "git clone" in text
    assert "docker compose up" in text
    assert "http://localhost:5173" in text
    assert "scripts/load_sample.py" in text
    assert "scripts/dump_sample.py" in text


def test_sample_scripts_compile():
    repo_root = Path(__file__).resolve().parents[3]
    load_script = repo_root / "scripts" / "load_sample.py"
    dump_script = repo_root / "scripts" / "dump_sample.py"

    assert load_script.exists()
    assert dump_script.exists()

    compile(load_script.read_text(encoding="utf-8"), str(load_script), "exec")
    compile(dump_script.read_text(encoding="utf-8"), str(dump_script), "exec")
