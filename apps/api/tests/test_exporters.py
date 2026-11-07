import json

import jsonschema

from hackproof.export.atlas import atlas_schema, write_atlas
from hackproof.export.stellarlight import stellarlight_schema, write_stellarlight
from tests.test_export import populated_export


async def test_stellarlight_and_atlas_exporters_validate_every_row_and_diff(
    scratch_db, tmp_path, capsys
):
    export = await populated_export(scratch_db)
    schema_dir = tmp_path / "schema"

    sl_rows = write_stellarlight(export, tmp_path, schema_dir)
    at_rows = write_atlas(export, tmp_path, schema_dir)

    assert len(sl_rows) == 1
    assert len(at_rows) == 1

    sl_schema = json.loads((schema_dir / "stellarlight.schema.json").read_text())
    at_schema = json.loads((schema_dir / "atlas.schema.json").read_text())
    assert sl_schema == stellarlight_schema()
    assert at_schema == atlas_schema()

    for row in sl_rows:
        jsonschema.validate(row, sl_schema)
    for row in at_rows:
        jsonschema.validate(row, at_schema)

    write_stellarlight(export, tmp_path, schema_dir, diff=True)
    write_atlas(export, tmp_path, schema_dir, diff=True)
    out = capsys.readouterr().out
    assert "stellarlight diff: +0 -0 ~0" in out
    assert "atlas diff: +0 -0 ~0" in out
