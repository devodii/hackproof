from hackproof.config import ROOT
from hackproof.export.files import ProjectFile
from hackproof.export.restore import FROM_DATABASE, RESTORED, load_files, restore


def test_every_exported_section_is_either_restored_or_read_from_the_database():
    fields = set(ProjectFile.model_fields)

    assert fields == set(RESTORED) | FROM_DATABASE, (
        "A new field on the project files must be added to RESTORED when the database "
        "cannot rebuild it, or to FROM_DATABASE when it can. Otherwise the data sync "
        "would delete it from the files."
    )


async def test_restoring_the_committed_files_brings_back_their_scan_data(scratch_db):
    files = load_files(ROOT / "data")
    assert files

    await restore(scratch_db, files)
    await restore(scratch_db, files)

    expected = {
        key: sum(len(entry.evidence) for p in files for entry in getattr(p, key))
        for key in RESTORED
    }
    tables = {
        "integrations": "repo_integrations",
        "tools": "repo_tools",
        "agents": "repo_agents",
    }
    for key, table in tables.items():
        found = await scratch_db.fetchval(f"SELECT count(*) FROM {table}")  # noqa: S608
        assert found == expected[key]


def test_a_file_url_goes_back_to_the_repo_path():
    from hackproof.export.restore import path_of

    repo = "https://github.com/a/b"
    assert path_of(repo, f"{repo}/blob/HEAD/src/x%20y.ts") == "src/x y.ts"
    assert path_of(repo, "https://demo.vercel.app/x") == "https://demo.vercel.app/x"
    assert path_of(repo, None) == ""
