from hackproof.sample import (
    default_sample_path,
    format_insert_block,
    sanitize_contributor_row,
    sanitize_repo_row,
)


def test_sample_sql_file_contains_ten_projects_and_twenty_contracts():
    path = default_sample_path()
    assert path.exists()
    sql = path.read_text(encoding="utf-8")
    assert "INSERT INTO projects" in sql
    assert "INSERT INTO contracts" in sql
    assert sql.count("'repo:") == 10
    assert sql.count("'CSAMPLECONTRACT") >= 20
    assert "avatar" not in sql.split("VALUES")[1].lower()


def test_sanitize_strips_personal_profile_fields():
    repo = {
        "full_name": "ygk94/4ward",
        "owner": "ygk94",
        "owner_avatar": "https://avatars.githubusercontent.com/u/1",
        "owner_location": "Lisbon",
        "country": "PT",
    }
    cleaned_repo = sanitize_repo_row(repo)
    assert cleaned_repo["owner"] == "ygk94"
    assert cleaned_repo["owner_avatar"] is None
    assert cleaned_repo["owner_location"] is None
    assert cleaned_repo["country"] is None

    contributor = {
        "full_name": "ygk94/4ward",
        "login": "ygk94",
        "avatar_url": "https://avatars.githubusercontent.com/u/1",
        "contributions": 96,
    }
    cleaned_contributor = sanitize_contributor_row(contributor)
    assert cleaned_contributor["login"] == "ygk94"
    assert cleaned_contributor["avatar_url"] is None


def test_format_insert_block_escapes_and_renders_conflict_clause():
    rows = [{"project_id": "repo:a/b", "contracts": 2, "tier": "verified"}]
    sql = format_insert_block(
        "projects", ["project_id", "contracts", "tier"], rows, ["project_id"]
    )
    assert "INSERT INTO projects (project_id, contracts, tier) VALUES" in sql
    assert "('repo:a/b', 2, 'verified')" in sql
    assert "ON CONFLICT (project_id) DO NOTHING;" in sql
