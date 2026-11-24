from trawl.schema.manifest import manifest_text

from hackproof.db_utils import pgschema
from hackproof.linking.methods import LinkMethod


def test_the_committed_manifest_matches_the_schema_files():
    committed = (pgschema.SCHEMA_DIR / "manifest.sql").read_text()

    assert committed == manifest_text(pgschema.SCHEMA_DIR)


def test_the_target_points_at_this_projects_database_files():
    assert pgschema.TARGET.schema_dir == pgschema.SCHEMA_DIR
    assert pgschema.TARGET.migrations_dir == pgschema.MIGRATIONS_DIR


async def test_the_sql_method_rank_follows_the_python_order(scratch_db):
    for position, method in enumerate(LinkMethod, start=1):
        assert await scratch_db.fetchval("SELECT method_rank($1)", method) == position
    assert await scratch_db.fetchval("SELECT method_rank('unknown')") is None
