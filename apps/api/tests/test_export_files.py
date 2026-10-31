import jsonschema
import pytest
import yaml

from hackproof.export.build import build_export
from hackproof.export.files import (
    SCHEMA_FILE,
    file_names,
    file_schema,
    project_file,
    to_file_yaml,
    write_project_files,
)
from hackproof.hackathon import get_hackathon
from hackproof.linking.reconcile import reconcile
from tests.helpers import STELLAR, add_repo
from tests.test_export import populated_export


def keys(value):
    if isinstance(value, dict):
        return set(value) | {inner for item in value.values() for inner in keys(item)}
    if isinstance(value, list):
        return {inner for item in value for inner in keys(item)}

    return set()


async def likely_export(db, *names):
    for name in names:
        await add_repo(db, name, window_commits=7, dependencies=STELLAR)
    await reconcile(db)

    return await build_export(db, get_hackathon(), ["likely", "possible"])


async def test_a_project_file_validates_and_keeps_only_public_facts(scratch_db):
    export = await populated_export(scratch_db)
    [project] = export.projects

    text = to_file_yaml(project_file(export.hackathon.slug, project))
    data = yaml.safe_load(text)

    jsonschema.validate(data, file_schema())
    assert text.startswith("# yaml-language-server: $schema=../schema-hackathon-project.yml\n")
    assert data["canonical_id"] == "pkg:github/team/app"
    assert data["contributors"] == [{"login": "ana", "contributions": 12}]
    assert data["chain"]["accounts"] == ["GDEPLOYER"]
    assert not {"avatar_url", "country", "stars", "forks"} & keys(data)


async def test_unknown_values_are_left_out_but_unknown_versions_are_kept(scratch_db):
    export = await populated_export(scratch_db)
    [project] = export.projects
    project = project.model_copy(
        update={"description": None, "stack_versions": {"@stellar/stellar-sdk": None}}
    )

    data = yaml.safe_load(to_file_yaml(project_file("hackmeridian-2026", project)))

    assert "description" not in data
    assert data["stack"] == {"@stellar/stellar-sdk": None}


async def test_file_names_are_lowercase_with_hyphens(scratch_db):
    export = await likely_export(scratch_db, "team/Stellar_Split", "team/Hack.Pay")

    assert sorted(file_names(export.projects).values()) == ["hack-pay", "stellar-split"]


async def test_colliding_names_are_prefixed_with_the_owner(scratch_db):
    export = await likely_export(scratch_db, "ana/koul", "Bo/koul", "cy/unique")

    assert file_names(export.projects) == {
        "ana/koul": "ana-koul",
        "Bo/koul": "bo-koul",
        "cy/unique": "unique",
    }


async def test_a_name_without_letters_or_digits_is_an_error(scratch_db):
    export = await likely_export(scratch_db, "team/___")

    with pytest.raises(ValueError, match="no usable file name"):
        file_names(export.projects)


async def test_writing_files_replaces_stale_ones_and_writes_the_schema(scratch_db, tmp_path):
    export = await likely_export(scratch_db, "team/app")
    year = tmp_path / str(export.hackathon.starts_at.year)
    year.mkdir()
    (year / "gone.yml").write_text("event: old\n")

    count = write_project_files(export, tmp_path)

    assert count == 1
    assert [path.name for path in year.glob("*.yml")] == ["app.yml"]
    jsonschema.validate(yaml.safe_load((year / "app.yml").read_text()), file_schema())
    assert yaml.safe_load((tmp_path / SCHEMA_FILE).read_text())["title"] == "ProjectFile"
